from odoo import api, fields, models


class WellnessDashboard(models.Model):
    """
    Singleton model for aggregating daily wellness pulse data.

    Fields are stored (not computed) so the board always reads real values
    even when opening in "new record" mode without a res_id.
    Values are refreshed via _refresh_pulse() on every read() and default_get().
    """

    _name = "wellness.dashboard"
    _description = "Wellness Snapshot Aggregator"

    participation_today = fields.Integer(string="Participants Today")
    avg_mood_today = fields.Float(string="Daily Mood Score", digits=(12, 1))
    sign_today = fields.Char(string="Pulse Sign")
    happy_percent = fields.Integer(string="Happy %")
    neutral_percent = fields.Integer(string="Neutral %")
    sad_percent = fields.Integer(string="Sad %")

    # Relationship for embedding graph in form view (OCA compliant dashboard)
    history_ids = fields.One2many(
        "wellness.check",
        compute="_compute_history_ids",
        string="Check History",
    )

    def _compute_history_ids(self):
        """Fetch all records to display in the integrated chart."""
        checks = self.env["wellness.check"].search([], order="date asc")
        for record in self:
            record.history_ids = checks

    # ------------------------------------------------------------------
    # Always refresh before READING an existing record
    # ------------------------------------------------------------------
    def read(self, fields_list=None, load="_classic_read"):
        self._refresh_pulse()
        return super().read(fields_list, load=load)

    # ------------------------------------------------------------------
    # Always populate when the form opens a NEW (empty) record
    # This is what the board calls - it opens form with no res_id
    # ------------------------------------------------------------------
    @api.model
    def default_get(self, fields_list):
        """Return real KPI values instead of empty defaults."""
        self._refresh_pulse()
        singleton = self.search([], limit=1)
        if singleton:
            res = {}
            for f in fields_list:
                val = getattr(singleton, f, False)
                if val is not None:
                    res[f] = val
            return res
        return super().default_get(fields_list)

    @api.model
    def _refresh_pulse(self):
        """
        Recomputes and STORES today's pulse metrics into the singleton.
        Falls back to the most recent date with data when today is empty.
        """
        singleton = self.search([], limit=1)
        if not singleton:
            return

        today = fields.Date.today()
        checks = self.env["wellness.check"].search([("date", "=", today)])

        # Fallback: use the most recent date with data
        if not checks:
            latest = self.env["wellness.check"].search([], order="date desc", limit=1)
            if latest:
                checks = self.env["wellness.check"].search([("date", "=", latest.date)])

        participation = len(checks)
        avg_mood = (
            sum(checks.mapped("mood_score")) / participation
            if participation > 0
            else 0.0
        )

        happy_count = len(checks.filtered(lambda r: r.sentiment == "happy"))
        neutral_count = len(checks.filtered(lambda r: r.sentiment == "neutral"))
        sad_count = len(checks.filtered(lambda r: r.sentiment == "sad"))

        total = participation or 1
        happy_p = int((happy_count / total) * 100)
        neutral_p = int((neutral_count / total) * 100)
        sad_p = 100 - happy_p - neutral_p if participation > 0 else 0

        sign = "="
        if happy_count > sad_count:
            sign = "+"
        elif sad_count > happy_count:
            sign = "-"

        # Use sudo().write() to avoid infinite loops via read()
        singleton.sudo().with_context(skip_refresh=True).write(
            {
                "participation_today": participation,
                "avg_mood_today": round(avg_mood, 1),
                "sign_today": sign,
                "happy_percent": happy_p,
                "neutral_percent": neutral_p,
                "sad_percent": sad_p,
            }
        )
