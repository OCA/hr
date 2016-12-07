# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_search_imposed_parameters(self, employee):
        """ """
        res = [('company_id', '=', employee.company_id.id),
               ('employee_ids', '=', False),  # no employee defined means all
               ('date_from', '>=', fields.Datetime.now())
               ]
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        """ add imposed days if a configuration exists """
        imposed_holiday = self.env['hr.holidays.imposed']
        holiday = self.env['hr.holidays']

        emp = super(HrEmployee, self).create(values)

        imposed = imposed_holiday.search(
            self._get_search_imposed_parameters(emp)
            )

        for imposed_day in imposed:
            created = holiday.create({
                'number_of_days_temp': 1.,
                'name': imposed_day.name,
                'date_from': imposed_day.date_from,
                'date_to': imposed_day.date_to,
                'employee_id': emp.id,
                'type': 'remove',
                'holiday_status_id': imposed_day.status_id.id,
                })
            if imposed_day.auto_confirm:
                created.signal_workflow('validate')

        return emp
