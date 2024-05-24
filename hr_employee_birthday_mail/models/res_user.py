# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class User(models.Model):
    _inherit = ["res.users"]

    allow_birthday_wishes = fields.Boolean(
        related="employee_id.allow_birthday_wishes", readonly=False, related_sudo=False
    )
    notify_others_birthday = fields.Boolean(
        related="employee_id.notify_others_birthday", readonly=False, related_sudo=False
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "allow_birthday_wishes",
            "notify_others_birthday",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "allow_birthday_wishes",
            "notify_others_birthday",
        ]
