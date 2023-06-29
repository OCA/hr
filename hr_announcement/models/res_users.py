# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def announcement_user_count(self):
        res = super().announcement_user_count()
        department_announcements = self.env["announcement"].search_read(
            [
                ("announcement_type", "=", "department"),
                ("in_date", "=", True),
                ("id", "not in", self.env.user.read_announcement_ids.ids),
            ],
            ["department_ids"],
        )
        announcements = self.env["announcement"].browse(
            [
                announcement["id"]
                for announcement in department_announcements
                if any(
                    department_id
                    in self.env["hr.department"]
                    .search([("member_ids.user_id", "!=", False)])
                    .ids
                    for department_id in announcement["department_ids"]
                )
            ]
        )

        position_announcements = self.env["announcement"].search_read(
            [
                ("announcement_type", "=", "job_position"),
                ("in_date", "=", True),
                ("id", "not in", self.env.user.read_announcement_ids.ids),
            ],
            ["position_ids"],
        )
        announcements += self.env["announcement"].browse(
            [
                announcement["id"]
                for announcement in position_announcements
                if any(
                    position_id
                    in self.env["hr.job"]
                    .search([("employee_ids.user_id", "!=", False)])
                    .ids
                    for position_id in announcement["position_ids"]
                )
            ]
        )
        return res + [
            {
                "id": announcement.id,
                "name": announcement.name,
                "content": announcement.content,
            }
            for announcement in announcements.sorted(lambda k: k.sequence)
        ]
