# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('user_id')
    def _compute_display_personal_data(self):
        for employee in self:
            employee.employee_display_personal_data = False
            if self.user_has_groups('hr.group_hr_user'):
                employee.employee_display_personal_data = True
            elif employee.user_id == self.env.user:
                employee.employee_display_personal_data = True

    employee_display_personal_data = fields.Boolean(
        compute='_compute_display_personal_data'
    )
