#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyrigth (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

from report import report_sxw

import logging
_l = logging.getLogger(__name__)

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'summarize': self.summerize,
            'sum_total': self.sum_total,
            'sum_difference': self.sum_difference,
            'sum_amount': self.sum_amount,
        })
        
        self.start_date = False
        self.end_date = False
        self.state = 'all'
        self.count = 0
        self.sum = 0
        self.difference = 0
        self.price = 0.22
    
    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('start_date', False):
            self.start_date = data['form']['start_date']
        if data.get('form', False) and data['form'].get('end_date', False):
            self.end_date = data['form']['end_date']
        if data.get('form', False) and data['form'].get('state', 'all'):
            self.state = data['form']['state']
        
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)
    
    def summerize(self, department_id):
        
        self.sum = 0
        self.difference = 0
        self.sum_amount = 0
        
        sheet_obj = self.pool.get('hr.bunching.sheet')
        
        if self.state == 'all':
            domain = []
        else:
            domain = [('state', '=', self.state)]
        domain = domain + [('department_id', '=', department_id),
                           '&', ('name', '>=', self.start_date),
                                ('name', '<=', self.end_date),
        ]
        sheet_ids = sheet_obj.search(self.cr, self.uid, domain)
        res = []
        seen_ids = []
        if len(sheet_ids) > 0:
            for sheet in sheet_obj.browse(self.cr, self.uid, sheet_ids):
                for line in sheet.line_ids:
                    if line.employee_id.id not in seen_ids:
                        res.append({'name': line.employee_id.name,
                                    'id': line.employee_id.id,
                                    'days_over_quota': line.difference > 0 and 1 or 0,
                                    'days': line.total > 0 and 1 or 0,
                                    'total': line.total,
                                    'difference': line.difference > 0 and line.difference or 0,
                                    'amount': line.difference > 0 and line.difference * self.price or 0})
                        seen_ids.append(line.employee_id.id)
                        self.sum += line.total
                        self.difference += line.difference > 0 and line.difference or 0
                        self.sum_amount += line.difference > 0 and line.difference * self.price or 0
                    else:
                        for r in res:
                            if r['id'] != line.employee_id.id:
                                continue
                            r['days_over_quota'] += line.difference > 0 and 1 or 0
                            r['days'] += line.total > 0 and 1 or 0
                            r['total'] += line.total
                            r['difference'] += line.difference > 0 and line.difference or 0
                            r['amount'] += line.difference > 0 and line.difference * self.price or 0
                            self.sum += line.total
                            self.difference += line.difference > 0 and line.difference or 0
                            self.sum_amount += line.difference > 0 and line.difference * self.price or 0
                            break
        
        return res
    
    def sum_total(self):
        return self.sum
    
    def sum_difference(self):
        return self.difference
    
    def sum_amount(self):
        return self.sum_amount
