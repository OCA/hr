from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MONTHS = [
    ("1", "January"),
    ("2", "February"),
    ("3", "March"),
    ("4", "April"),
    ("5", "May"),
    ("6", "June"),
    ("7", "July"),
    ("8", "August"),
    ("9", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December"),
]


class ResourceCalendarSeason(models.Model):
    _name = "resource.calendar.season"
    _description = "Resource Calendar Season"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Seasonal Calendar",
        required=True,
        ondelete="cascade",
    )
    season_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
        ondelete="restrict",
        help="Working time applied during this season.",
    )
    month_from = fields.Selection(MONTHS, string="From Month", required=True)
    month_to = fields.Selection(MONTHS, string="To Month", required=True)

    @api.constrains("month_from", "month_to", "calendar_id")
    def _check_no_overlap(self):
        for calendar in self.mapped("calendar_id"):
            coverage = {}
            for season in calendar.season_ids:
                for month in season._covered_months():
                    if month in coverage:
                        raise ValidationError(
                            _(
                                "Seasons %(first)s and %(second)s overlap.",
                                first=coverage[month].name,
                                second=season.name,
                            )
                        )
                    coverage[month] = season

    def _covered_months(self):
        """Return the set of month numbers covered by the season, handling
        ranges that wrap around the year end (e.g. December to January)."""
        self.ensure_one()
        start = int(self.month_from)
        end = int(self.month_to)
        if start <= end:
            return set(range(start, end + 1))
        return set(range(start, 13)) | set(range(1, end + 1))

    def _contains_date(self, day):
        self.ensure_one()
        return day.month in self._covered_months()
