# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _get_search_imposed_parameters(self):
        self.ensure_one()
        res = [('company_id', '=', self.company_id.id),
               ('employee_ids', '=', False),  # no employee defined means all
               ('date_from', '>=', fields.Datetime.now())
               ]
        return res

    @api.model
    def create(self, values):
        """ add imposed days if a configuration exists """

        employee = super(HrEmployee, self).create(values)

        imposed = self.env['hr.holidays.imposed'].search(
            employee._get_search_imposed_parameters()
        )
        for imposed_day in imposed:
            leave_vals = imposed_day._prepare_leave_from_imposed_day()
            leave_vals.update({'employee_id': employee.id})
            created_leave = self.env['hr.holidays'].create(leave_vals)
            if imposed_day.auto_confirm:
                created_leave.action_validate()

        return employee
