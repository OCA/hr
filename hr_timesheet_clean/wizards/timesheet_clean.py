# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import calendar

from odoo import _, fields, models


class TimesheetClean(models.TransientModel):
    """
    Wizard used to clean timesheets
    """

    _name = "timesheet.clean"
    _description = "Timesheet clean"

    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            day=calendar.monthrange(
                fields.Date.context_today(self).year,
                fields.Date.context_today(self).month,
            )[1]
        ),
    )

    def action_clean(self):
        self._action_clean()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Empty timesheet lines"),
                "message": _("Empty timesheet lines cleaned"),
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def _action_clean(self):
        return (
            self.env["account.analytic.line"]
            .search(
                [
                    ("date", "<=", self.date_to),
                    ("date", ">=", self.date_from),
                    ("unit_amount", "=", 0),
                    (
                        "project_id",
                        "!=",
                        False,
                    ),  # This determine if it's timesheet line
                ]
            )
            .unlink()
        )
