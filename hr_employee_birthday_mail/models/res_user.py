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

    def __init__(self, pool, cr):
        """Override of __init__ to add access rights.
        Access rights are disabled by default, but allowed
        on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        super(User, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + [
            "allow_birthday_wishes",
            "notify_others_birthday",
        ]
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + [
            "allow_birthday_wishes",
            "notify_others_birthday",
        ]
