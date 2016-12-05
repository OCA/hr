# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        """ add imposed days if a configuration exists """
        imposed_holiday = self.env['hr.holidays.imposed']
        holiday = self.env['hr.holidays']

        emp = super(HrEmployee, self).create(values)
        company = emp.company_id.id

        imposed = imposed_holiday.search(
            [('company_id', '=', company),
             ('employee_ids', '=', False),  # no employee defined means all
             ]
            )

        if imposed:
            for imposed_day in imposed:
                created = holiday.create({
                    'number_of_days_temp': 1.,
                    'name': imposed_day.name,
                    'date_from': imposed_day.date,
                    'date_to': imposed_day.date,
                    'employee_id': emp.id,
                    'type': 'remove',
                    'holiday_status_id': imposed_day.status_id.id,
                    })
                if imposed_day.auto_confirm:
                    created.signal_workflow('validate')

        return emp
