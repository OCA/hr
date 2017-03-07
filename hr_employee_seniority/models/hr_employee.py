# -*- coding: utf-8 -*-
# copyright 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar
from dateutil.relativedelta import relativedelta

from odoo import api, exceptions, fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    initial_employment_date = fields.Date(
        string='Initial Date of Employment',
        help='Date of first employment if it was before the start of the '
             'first contract in the system.',
    )
    length_of_service = fields.Float(
        'Months of Service',
        compute='_compute_months_service',
    )

    def _first_contract(self):
        Contract = self.env['hr.contract']
        return Contract.search([('employee_id', '=', self.id)],
                               order='date_start asc', limit=1)

    @staticmethod
    def check_next_days(date_to, date_from):
        if date_from.day == 1:
            days_in_month = calendar.monthrange(date_to.year, date_to.month)[1]
            if date_to.day == days_in_month:
                return 1
            elif date_from.day == date_to.day + 1:
                return 1
        return 0

    @api.depends('contract_ids', 'initial_employment_date')
    def _compute_months_service(self):
        date_now = fields.Date.today()
        for employee in self:
            nb_month = 0

            if employee.initial_employment_date:
                if employee.contract_ids:
                    contract = employee._first_contract()
                    to_dt = fields.Date.from_string(contract.date_start)
                else:
                    to_dt = fields.Date.from_string(date_now)

                from_dt = fields.Date.from_string(
                    employee.initial_employment_date)

                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                    relativedelta(to_dt, from_dt).months + \
                    self.check_next_days(to_dt, from_dt)

            for contract in employee.contract_ids:
                from_dt = fields.Date.from_string(contract.date_start)
                if contract.date_end and contract.date_end < date_now:
                    to_dt = fields.Date.from_string(contract.date_end)
                else:
                    to_dt = fields.Date.from_string(date_now)
                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                    relativedelta(to_dt, from_dt).months + \
                    self.check_next_days(to_dt, from_dt)

            employee.length_of_service = nb_month

    @api.constrains('initial_employment_date', 'contract_ids')
    def _check_initial_employment_date(self):
        if self.initial_employment_date and len(self.contract_ids):
            initial_dt = fields.Date.from_string(self.initial_employment_date)
            first_contract_dt = fields.Date.from_string(
                self._first_contract().date_start)
            if initial_dt > first_contract_dt:
                raise exceptions.UserError("The initial employment date cannot"
                                           " be after the first contract in "
                                           "the system!")
