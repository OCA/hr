# -*- coding:utf-8 -*-
import operator
from functools import partial
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from openerp import fields, models, _, api
from openerp.exceptions import Warning, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    initial_employment_date = fields.Date('Initial Date of Employment',
        help='Date of first employment if it was before the start of the '
             'first contract in the system.',
    )
    date_start = fields.Date('Start Date', readonly=True, store=True, 
                             compute='_compute_service_details')    
    
    length_of_service = fields.Float('Length of Service', readonly=True, 
                                     compute='_compute_employment_length')
    length_of_service_str = fields.Char('Length of Service', readonly=True, 
                                     compute='_compute_employment_length')
    
    @api.one
    @api.constrains('initial_employment_date', 'first_contract_id')
    def _check_initial_employment_date(self):
        if self.initial_employment_date and self.first_contract_id:
            if fields.Date.from_string(self.initial_employment_date) > \
            fields.Date.from_string(self.first_contract_id.date_start):
                raise ValidationError("The initial employment date cannot be "
                      "after the first contract in the system.\n")
    
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
        if not len(self.contract_ids): # if employee has no contracts
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
                deltas.append(relativedelta(fields.Date.
                  from_string(self.first_contract_id.date_start), dt_date_start))
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
            first_contract = self.first_contract_id
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
    def _compute_employment_length(self):
        dt =  'date_now' in self.env.context and self.env.context['date_now']\
                or fields.Date.today()
            
        delta = self.get_service_length_delta_at_time(dt)
        if not delta:
            return
        self.length_of_service = float(((delta.years * 12) + delta.months))\
         + delta.days/30.0
        self.length_of_service_str = self._convert_timedelta_to_str(delta)