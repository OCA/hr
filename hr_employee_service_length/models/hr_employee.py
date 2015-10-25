# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import operator
from functools import partial
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp import fields, models, api
from openerp.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    initial_employment_date = fields.Date(
        help='Date of first employment if it was before the start of the '
             'first contract in the system.',
    )
    date_start = fields.Date(
        'Start Date',
        readonly=True,
        store=True,
        compute='_compute_service_details'
    )
    length_of_service = fields.Float(
        'Length of Service',
        readonly=True,
        compute='_compute_employment_length'
    )
    length_of_service_str = fields.Char(
        'Length of Service',
        readonly=True,
        compute='_compute_employment_length'
    )

    def _first_contract(self):
        return self.contract_ids\
            .sorted(key=operator.itemgetter('date_start', 'id'))[0]

    @api.one
    @api.constrains('initial_employment_date', 'contract_ids')
    def _check_initial_employment_date(self):
        if self.initial_employment_date and len(self.contract_ids):
            initial_dt = fields.Date.from_string(self.initial_employment_date)
            first_contract_dt = fields.Date.from_string(
                self._first_contract().date_start)
            if initial_dt > first_contract_dt:
                raise ValidationError("The initial employment date cannot be "
                                      "after the first contract in the system")

    @staticmethod
    def _get_contract_interval(contract, dt_ref=None):
        if not dt_ref:
            dt_ref = date.today()
        end_date = dt_ref
        if contract.date_end:
            end_date = fields.Date.from_string(contract.date_end)
            if end_date >= dt_ref:
                end_date = dt_ref
        return relativedelta(end_date,
                             fields.Date.from_string(contract.date_start))

    def get_service_length_delta_at_time(self, dt=None):
        '''
        get's the service length for an employee at a specific date
        '''
        if not self.date_start:
            return False
        if not dt:
            dt_today = date.today()
        else:
            dt_today = isinstance(dt, date) and dt \
                or fields.Date.from_string(dt)
        dt_date_start = fields.Date.from_string(self.date_start)
        mapfunc = partial(self._get_contract_interval, dt_ref=dt_today)
        delta = relativedelta(dt_today, dt_today)
        if not len(self.contract_ids):  # if employee has no contracts
            delta = relativedelta(dt_today, dt_date_start)
        else:
            # if employee has contracts let's first find the months for which
            # employee has been employed according to the contracts
            deltas = self.contract_ids \
                .sorted(key=operator.itemgetter('date_start', 'id')) \
                .mapped(mapfunc)

            # if initial employment date is before the first contract date then
            # let's take the difference into account
            if self.date_start == self.initial_employment_date:
                first_contract_dt = fields.Date.from_string(
                    self._first_contract().date_start)
                deltas.append(relativedelta(first_contract_dt, dt_date_start))
            for d in deltas:
                delta += d
        return delta

    @api.one
    @api.depends('contract_ids', 'initial_employment_date',
                 'contract_ids.date_start', 'contract_ids.employee_id')
    def _compute_service_details(self):
        date_start = False
        first_contract = False
        if not len(self.contract_ids):
            if not self.initial_employment_date:
                return
            else:
                date_start = self.initial_employment_date
        else:
            first_contract = self._first_contract()
            date_start = first_contract.date_start
            if self.initial_employment_date \
                and fields.Date.from_string(first_contract.date_start) \
                    > fields.Date.from_string(self.initial_employment_date):
                date_start = self.initial_employment_date
        self.date_start = date_start

    @staticmethod
    def _convert_timedelta_to_str(delta):
        str_since = ''
        year_label = delta.years > 1 and 'yrs' or 'yr'
        month_label = delta.months > 1 and 'mnths' or 'mnth'
        year_str = month_str = ''
        if delta.years:
            year_str = '%s %s' % (delta.years, year_label)

        if delta.months:
            month_str = '%s %s' % (delta.months, month_label)

        str_since += year_str
        if year_str and month_str:
            str_since += ' and ' + month_str
        elif month_str:
            str_since += month_str
        return str_since

    @api.one
    @api.depends('date_start')
    def _compute_employment_length(self):
        '''
        employment length inn years
        '''
        dt = ('date_now' in self.env.context and self.env.context['date_now']
              or fields.Date.today())

        delta = self.get_service_length_delta_at_time(dt)
        if not delta:
            return 0
        self.length_of_service = delta.years + (delta.months/12.0) + (
            delta.days/365.25)
        self.length_of_service_str = self._convert_timedelta_to_str(delta)
