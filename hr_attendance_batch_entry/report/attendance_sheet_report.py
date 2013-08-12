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
from dateutil.relativedelta import relativedelta

from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_no': self._get_no,
            'week_start': self._get_week_start,
            'week_no': self._get_week_no,
            'mday': self._get_mday,
        })
        
        self.no = 0
        self.department_id = 0
    
    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('week_start', False):
            self.week_start = data['form']['week_start']
        else:
            self.week_start = (datetime.now().date() + relativedelta(days= +(7 - datetime.now().date().weekday()))).strftime('%Y-%m-%d')
        
        if data.get('form', False) and data['form'].get('week_no'):
            self.week_no = data['form']['week_no']
        else:
            self.week_no = datetime.strptime(self.week_start, '%Y-%m-%d').isocalendar()[1]
        
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_week_start(self):
        dt = datetime.strptime(self.week_start, '%Y-%m-%d')
        return dt.strftime('%B %d, %Y')
    
    def _get_week_no(self):
        return self.week_no
    
    def _get_no(self, d_id):
        if d_id != self.department_id:
            self.department_id = d_id
            self.no = 0
        self.no += 1
        return self.no
    
    def _get_mday(self, wday):
        dt = datetime.strptime(self.week_start, '%Y-%m-%d')
        dt = dt + relativedelta(days= +wday)
        return dt.strftime('%d')
