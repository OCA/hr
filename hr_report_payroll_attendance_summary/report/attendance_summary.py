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
            'get_employee_data': self.get_employee_data,
            'get_worked_days': self.get_worked_days,
            'get_daily_ot': self.get_daily_ot,
            'get_nightly_ot': self.get_nightly_ot,
            'get_restday_ot': self.get_restday_ot,
            'get_holiday_ot': self.get_holiday_ot,
            'get_bunch_no': self.get_bunch_no,
            'get_awol': self.get_awol,
            'get_sickleave': self.get_sickleave,
            'get_no': self.get_no,
            'get_start': self.get_start,
            'get_end': self.get_end,
            'lose_bonus': self.lose_bonus,
            'get_paid_leave': self.get_paid_leave,
            'get_employee_list': self.get_employee_list,
        })

        self.start_date = False
        self.end_date = False
        self.ee_lines = {}
        self.no = 0
        self.department_id = False
        self.regular_hours = 8.0

    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('start_date', False):
            self.start_date = data['form']['start_date']
        if data.get('form', False) and data['form'].get('end_date', False):
            self.end_date = data['form']['end_date']

        return super(Parser, self).set_context(
            objects, data, ids, report_type=report_type)

    def get_employee_list(self, department_id):

        ee_obj = self.pool.get('hr.employee')
        ee_ids = ee_obj.search(
            self.cr, self.uid, [
                ('active', '=', True),
                '|',
                ('department_id.id', '=', department_id),
                ('saved_department_id.id', '=', department_id)
                ])
        ees = ee_obj.browse(self.cr, self.uid, ee_ids)
        return ees

    def get_employee_data(self, department_id):

        payslip_obj = self.pool.get('hr.payslip')
        ee_obj = self.pool.get('hr.employee')

        dtStart = datetime.strptime(self.start_date, OE_DATEFORMAT).date()
        dtEnd = datetime.strptime(self.end_date, OE_DATEFORMAT).date()
        ee_ids = ee_obj.search(
            self.cr, self.uid, [
                ('active', '=', True),
                '|',
                ('department_id.id', '=', department_id),
                ('saved_department_id.id', '=', department_id)
                ])
        for ee in ee_obj.browse(self.cr, self.uid, ee_ids):
            datas = []
            for c in ee.contract_ids:
                dtCStart = False
                dtCEnd = False
                if c.date_start:
                    dtCStart = datetime.strptime(
                        c.date_start, OE_DATEFORMAT).date()
                if c.date_end:
                    dtCEnd = datetime.strptime(
                        c.date_end, OE_DATEFORMAT).date()
                if (dtCStart and dtCStart <= dtEnd) and (
                    (dtCEnd and dtCEnd >= dtStart) or not dtCEnd
                ):
                    datas.append({
                        'contract_id': c.id,
                        'date_start': (dtCStart > dtStart
                                       and dtCStart.strftime(OE_DATEFORMAT)
                                       or dtStart.strftime(OE_DATEFORMAT)),
                        'date_end': ((dtCEnd and dtCEnd < dtEnd)
                                     and dtCEnd.strftime(OE_DATEFORMAT)
                                     or dtEnd.strftime(OE_DATEFORMAT)),
                    })
            wd_lines = []
            for d in datas:
                wd_lines += payslip_obj.get_worked_day_lines(
                    self.cr, self.uid, [d['contract_id']],
                    d['date_start'], d['date_end'])

            self.ee_lines.update({ee.id: wd_lines})

    def get_start(self):
        return datetime.strptime(self.start_date, OE_DATEFORMAT).strftime(
            '%B %d, %Y')

    def get_end(self):
        return datetime.strptime(self.end_date, OE_DATEFORMAT).strftime(
            '%B %d, %Y')

    def get_no(self, department_id):

        if not self.department_id or self.department_id != department_id:
            self.department_id = department_id
            self.no = 1
        else:
            self.no += 1

        return self.no

    def get_employee_start_date(self, employee_id):

        first_day = False
        c_obj = self.pool.get('hr.contract')
        c_ids = c_obj.search(
            self.cr, self.uid, [('employee_id', '=', employee_id)])
        for contract in c_obj.browse(self.cr, self.uid, c_ids):
            if not first_day or contract.date_start < first_day:
                first_day = contract.date_start
        return first_day

    def get_worked_days(self, employee_id):

        total = 0.0
        maxw = 0.0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['WORK100']:
                total += float(line['number_of_hours']) / self.regular_hours
            elif line['code'] == ['MAX']:
                maxw += float(line['number_of_hours']) / self.regular_hours
        total += self.get_paid_leave(employee_id)
        awol = self.get_awol(employee_id)

        # Take care to identify and handle employee's who didn't work the
        # full month: newly hired and terminated employees
        #
        hire_date = self.get_employee_start_date(employee_id)
        term_ids = self.pool.get(
            'hr.employee.termination').search(
                self.cr, self.uid, [
                    ('name', '<', self.end_date),
                    ('name', '>=', self.start_date),
                    ('employee_id', '=', employee_id),
                    ('employee_id.status', 'in', [
                        'pending_inactive', 'inactive']),
                    ('state', 'not in', ['cancel'])])

        if hire_date <= self.start_date and len(term_ids) == 0:
            if total >= maxw:
                total = 26
            total = total - awol
        return total

    def get_paid_leave(self, employee_id):

        total = 0
        paid_leaves = ['LVANNUAL', 'LVBEREAVEMENT', 'LVCIVIC', 'LVMATERNITY',
                       'LVMMEDICAL', 'LVPTO', 'LVWEDDING', 'LVSICK']
        for line in self.ee_lines[employee_id]:
            if line['code'] in paid_leaves:
                total += float(line['number_of_hours']) / self.regular_hours
        return total

    def get_daily_ot(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['WORKOTD']:
                total += line['number_of_hours']
        return total

    def get_nightly_ot(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['WORKOTN']:
                total += line['number_of_hours']
        return total

    def get_restday_ot(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['WORKOTR']:
                total += line['number_of_hours']
        return total

    def get_holiday_ot(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['WORKOTH']:
                total += line['number_of_hours']
        return total

    def get_bunch_no(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['BUNCH']:
                total += int(line['number_of_hours'])
        return total

    def get_awol(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['AWOL']:
                total += float(line['number_of_hours']) / self.regular_hours
        return total

    def get_sickleave(self, employee_id):

        total = 0
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['LVSICK']:
                total += float(line['number_of_hours']) / self.regular_hours
            elif line['code'] in ['LVSICK50']:
                total += float(line['number_of_hours']) * 0.5
        return total

    def lose_bonus(self, employee_id):

        loseit = False
        for line in self.ee_lines[employee_id]:
            if line['code'] in ['AWOL', 'TARDY', 'NFRA', 'WARN'] and line[
                'number_of_hours'
            ] > 0.01:
                loseit = True
        return loseit
