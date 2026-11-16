from datetime import date

from odoo import _, fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrEmployeeBirthdayCalendarReminder(TransactionCase):
    def test_cron_event_reminder(self):
        today = fields.Date.context_today(self.env["hr.employee"])
        employee = self.env["hr.employee"].create(
            {
                "name": "Birthday Person",
                "birthday": date(today.year, today.month, today.day),
            }
        )
        self.env["hr.employee"]._birthday_reminder()
        event = self.env["calendar.event"].search_count(
            [
                (
                    "name",
                    "ilike",
                    _("\U0001f389 Birthday reminder %s") % employee.name,
                ),
                ("start", "=", today),
                ("stop", "=", today),
            ]
        )
        self.assertGreaterEqual(event, 1)
