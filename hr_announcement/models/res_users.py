# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def announcement_user_count(self):
        res = super().announcement_user_count()

        user = self.env.user
        Announcement = self.env["announcement"]

        department_ids = user.employee_ids.mapped("department_id").ids
        position_ids = user.employee_ids.mapped("job_id").ids

        base_domain = [
            ("in_date", "=", True),
            ("id", "not in", user.read_announcement_ids.ids),
        ]

        announcements = Announcement

        if department_ids:
            announcements |= Announcement.search(
                base_domain
                + [
                    ("announcement_type", "=", "department"),
                    ("department_ids", "in", department_ids),
                ]
            )

        if position_ids:
            announcements |= Announcement.search(
                base_domain
                + [
                    ("announcement_type", "=", "job_position"),
                    ("position_ids", "in", position_ids),
                ]
            )

        return res + [
            {
                "id": announcement.id,
                "name": announcement.name,
                "content": announcement.content,
            }
            for announcement in announcements.sorted("sequence")
        ]
