# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    auto_approve = fields.Boolean(
        string='Auto Approve',
        help="If True, leaves belonging to this leave type will be"
             " automatically approved")
