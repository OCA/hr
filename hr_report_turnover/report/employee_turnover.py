# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
#

from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_hno': self.get_hno,
            'get_tno': self.get_tno,
            'get_start': self.get_start,
            'get_end': self.get_end,
            'get_hires': self.get_hires,
            'get_terminations': self.get_terminations,
            'get_total_terminations': self.get_sumt,
            'get_total_hires': self.get_sumh,
        })

        self.start_date = False
        self.end_date = False
        self.hno = 0
        self.tno = 0
        self.hdepartment_id = False
        self.tdepartment_id = False
        self.sumh = 0
        self.sumt = 0

    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('start_date', False):
            self.start_date = data['form']['start_date']
        if data.get('form', False) and data['form'].get('end_date', False):
            self.end_date = data['form']['end_date']

        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

    def get_start(self):
        return datetime.strptime(self.start_date, OE_DATEFORMAT).strftime('%B %d, %Y')

    def get_end(self):
        return datetime.strptime(self.end_date, OE_DATEFORMAT).strftime('%B %d, %Y')

    def get_hno(self, department_id):

        if not self.hdepartment_id or self.hdepartment_id != department_id:
            self.hdepartment_id = department_id
            self.hno = 1
        else:
            self.hno += 1

        return self.hno

    def get_tno(self, department_id):

        if not self.tdepartment_id or self.tdepartment_id != department_id:
            self.tdepartment_id = department_id
            self.tno = 1
        else:
            self.tno += 1

        return self.tno

    def get_hires(self, department_id, docount=False):

        res = []
        dStart = datetime.strptime(self.start_date, OE_DATEFORMAT)
        dEnd = datetime.strptime(self.end_date, OE_DATEFORMAT)
        department = self.pool.get('hr.department').browse(
            self.cr, self.uid, department_id)
        for ee in department.member_ids:
            # if there are no contracts or more than one contract assume
            # this is not a new employee
            if len(ee.contract_ids) == 0 or len(ee.contract_ids) > 1:
                continue
            d = datetime.strptime(ee.contract_id.date_start, OE_DATEFORMAT)
            if dStart <= d <= dEnd:
                res.append({'name': ee.name,
                            'f_employee_no': ee.f_employee_no,
                            'hire_date': ee.contract_id.date_start})
                if docount:
                    self.sumh += 1
        return res

    def get_terminations(self, department_id, docount=False):

        res = []
        seen_ids = []
        term_obj = self.pool.get('hr.employee.termination')
        term_ids = term_obj.search(
            self.cr, self.uid, [('name', '>=', self.start_date),
                                ('name', '<=', self.end_date), ])
        for term in term_obj.browse(self.cr, self.uid, term_ids):
            if term.employee_id.department_id:
                dept_id = term.employee_id.department_id.id
            elif term.employee_id.saved_department_id:
                dept_id = term.employee_id.saved_department_id.id
            else:
                dept_id = False
            if term.employee_id.id not in seen_ids and dept_id == department_id:
                res.append({'name': term.employee_id.name,
                            'f_employee_no': term.employee_id.f_employee_no,
                            'termination_date': term.name})
                seen_ids.append(term.employee_id.id)
        if docount:
            self.sumt += len(res)
        return res

    def get_sumh(self):
        return self.sumh

    def get_sumt(self):
        return self.sumt
