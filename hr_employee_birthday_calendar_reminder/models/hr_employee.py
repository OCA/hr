from odoo import _, api, fields, models


class HrEemployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _birthday_reminder(self):
        today = fields.Date.context_today(self)
        employees = self.search([("birthday", "!=", False)])

        birthday_employees = employees.filtered(
            lambda e: e.birthday.month == today.month and e.birthday.day == today.day
        )

        for employee in birthday_employees:
            existing = self.env["calendar.event"].search_count(
                [
                    (
                        "name",
                        "=",
                        _("\U0001f389 Birthday reminder %s") % employee.name,
                    ),
                    ("start", "=", today),
                    ("stop", "=", today),
                ]
            )
            if not existing:
                partner_ids = []

                if employee.parent_id:
                    partner_ids.append((4, employee.parent_id.work_contact_id.id))
                elif employee.work_contact_id:
                    partner_ids.append((4, employee.work_contact_id.id))

                self.env["calendar.event"].create(
                    {
                        "name": _("\U0001f389 Birthday reminder %s") % employee.name,
                        "start": today,
                        "stop": today,
                        "allday": True,
                        "partner_ids": partner_ids,
                    }
                )

        return True
