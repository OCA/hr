#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OEDATE_FORMAT
from openerp.tools.translate import _

class hr_payslip(osv.Model):
    
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        
        res = super(hr_payslip, self).get_worked_day_lines(cr, uid, contract_ids, date_from, date_to,
                                                           context=context)
        if len(res) == 0:
            return res
        
        # Use the first contract ID available
        contract_id = res[0]['contract_id']
        employee_id = self.pool.get('hr.contract').read(cr, uid, contract_id, ['employee_id'],
                                                        context=context)['employee_id'][0]
        ee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        
        dFrom = datetime.strptime(date_from, OEDATE_FORMAT).date()
        dTo = datetime.strptime(date_to, OEDATE_FORMAT).date()
        
        # Gather the following data
        #    1. Number of infractions for not taking care of equipment or for
        #       disregarding rules & regulations
        #    2. Number of written warnings
        #    3. Number of times late for work
        #
        
        # 1. Number of infractions
        nfra = {
             'name': _("Infractions"),
             'sequence': 100,
             'code': 'NFRA',
             'number_of_days': 0.0,
             'number_of_hours': 0.0,
             'contract_id': contract_id,
        }
        for infraction in ee.infraction_ids:
            d = datetime.strptime(infraction.date, OEDATE_FORMAT).date()
            if d >= dFrom and d <= dTo and infraction.category_id.code in ['CARE', 'RULE'] and infraction.state not in ['draft']:
                nfra['number_of_days'] += 1
                nfra['number_of_hours'] += 1
        
        # 2. Number of written warnings
        warn = {
             'name': _("Warnings"),
             'sequence': 101,
             'code': 'WARN',
             'number_of_days': 0.0,
             'number_of_hours': 0.0,
             'contract_id': contract_id,
        }
        for action in ee.infraction_action_ids:
            if action.warning_id and action.warning_id.type == 'written' and action.infraction_id and action.infraction_id.state == 'action':
                d = datetime.strptime(action.warning_id.date, OEDATE_FORMAT).date()
            if d >= dFrom and d <= dTo:
                warn['number_of_days'] += 1
                warn['number_of_hours'] += 1
        
        # 3. Number of times late for work
        tardy = {
             'name': _("Tardy"),
             'sequence': 102,
             'code': 'TARDY',
             'number_of_days': 0.0,
             'number_of_hours': 0.0,
             'contract_id': contract_id,
        }
        tardy_ids = self.pool.get('hr.schedule.alert').search(cr, uid,
                                                             [
                                                              ('employee_id', '=', employee_id),
                                                              ('rule_id.code', '=', 'TARDY'),
                                                              '&',
                                                                  ('name', '>=', date_from + ' 00:00:00'),
                                                                  ('name', '<=', date_to + ' 23:59:59'),
                                                             ])
        if tardy_ids > 0:
            tardy['number_of_days'] += len(tardy_ids)
            tardy['number_of_hours'] += tardy['number_of_days']
        
        res += [nfra] + [warn] + [tardy]
        return res
