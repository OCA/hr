# Copyright 2016-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    auto_approve_policy = fields.Selection(
        selection=[
            ('no', 'No auto Validation'),
            ('hr', 'Auto Validated by HR'),
            ('all', 'Auto Validated by Everyone'),
        ], default='no', required=True,
    )
