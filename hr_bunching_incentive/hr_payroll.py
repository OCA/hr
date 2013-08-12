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
        
        
        dFrom = datetime.strptime(date_from, OEDATE_FORMAT).date()
        dTo = datetime.strptime(date_to, OEDATE_FORMAT).date()
        
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            
            # Set the proper time frame
            #
            c_start = date_from
            c_end = date_to
            if contract.date_start:
                dc_start = datetime.strptime(contract.date_start, OEDATE_FORMAT).date()
                if dc_start > dFrom:
                    c_start = dc_start.strftime(OEDATE_FORMAT)
            if contract.date_end:
                dc_end = datetime.strptime(contract.date_end, OEDATE_FORMAT).date()
                if dc_end < dTo:
                    c_end = dc_end.strftime(OEDATE_FORMAT)
            
            # Gather the total number of extra bunches above quota
            #
            bunch = {
                 'name': _("Extra bunches graded"),
                 'sequence': 150,
                 'code': 'BUNCH',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            bsl_obj = self.pool.get('hr.bunching.sheet.line')
            bunching_ids = bsl_obj.search(cr, uid,
                                          [
                                           ('employee_id', '=', contract.employee_id.id),
                                           ('sheet_id.state', '=', 'approve'),
                                           '&',
                                               ('sheet_id.name', '>=', c_start),
                                               ('sheet_id.name', '<=', c_end),
                                          ],
                                          context=context)
            if bunching_ids > 0:
                for line in bsl_obj.browse(cr, uid, bunching_ids, context=context):
                    bunch['number_of_days'] += (line.difference > 0) and line.difference or 0
                    bunch['number_of_hours'] += (line.difference > 0) and line.difference or 0
            
            res += [bunch]
        
        return res
