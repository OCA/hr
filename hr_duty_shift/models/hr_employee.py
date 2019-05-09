# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    duty_shift_ids = fields.One2many(
        'hr.duty.shift',
        inverse_name='employee_id'
    )
