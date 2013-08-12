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
            'get_department_name': self._get_department_name,
        })
        
        self.no = 0
        self.department_id = 0
        self.department_name = ''
    
    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('department_id', False):
            self.department_id = data['form']['department_id']
            ddata = self.pool.get('hr.department').read(self.cr, self.uid, self.department_id,
                                                        ['complete_name'])
            self.department_name = ddata['complete_name']
        
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_department_name(self):
        return self.department_name
    
    def _get_no(self, d_id):
        if d_id != self.department_id:
            self.department_id = d_id
            self.no = 0
        self.no += 1
        return self.no
