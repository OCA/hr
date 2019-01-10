# Copyright 2016-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    auto_approve = fields.Boolean(
        string='Auto Validate',
        help="If True, leaves belonging to this leave type will be"
             " automatically validated")
