#-*- coding:utf-8 -*-
#
#
#    Copyrigth (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
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
#

from datetime import datetime, timedelta
from pytz import timezone, utc

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_no': self.get_no,
            'get_date': self.get_date,
            'get_present': self.get_present,
            'get_absent': self.get_absent,
            'get_restday': self.get_restday,
            'get_al': self.get_al,
            'get_sl': self.get_sl,
            'get_ml': self.get_ml,
            'get_ol': self.get_ol,
            'get_terminated': self.get_terminated,
            'get_tot_present': self.get_sum_present,
            'get_tot_absent': self.get_sum_absent,
            'get_tot_restday': self.get_sum_restday,
            'get_tot_al': self.get_sum_al,
            'get_tot_sl': self.get_sum_sl,
            'get_tot_ml': self.get_sum_ml,
            'get_tot_ol': self.get_sum_ol,
            'get_tot_terminated': self.get_sum_terminated,
        })

        self.LVCODES = [
            'LVBEREAVEMENT', 'LVWEDDING', 'LVMMEDICAL', 'LVPTO', 'LVCIVIC', 'LVSICK',
            'LVSICK50', 'LVSICK00', 'LVMATERNITY', 'LVANNUAL', 'LVTRAIN', 'LVUTO']

        self.date = False
        self.no = 0
        self._present = 0
        self._absent = 0
        self._restday = 0
        self._al = 0
        self._sl = 0
        self._ml = 0
        self._ol = 0
        self._terminated = 0

    def set_context(self, objects, data, ids, report_type=None):
        if data.get('form', False) and data['form'].get('date', False):
            self.date = data['form']['date']

        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

    def get_date(self):
        return datetime.strptime(self.date, OE_DATEFORMAT).strftime('%B %d, %Y')

    def get_no(self):

        self.no += 1
        return self.no

    def get_present_employees(self, department_id):

        att_obj = self.pool.get('hr.attendance')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dt = datetime.strptime(self.date + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdt = (local_tz.localize(dt, is_dst=False)).astimezone(utc)
        att_ids = att_obj.search(self.cr, self.uid,
                                 [('name', '>=', utcdt.strftime(OE_DATETIMEFORMAT)),
                                  ('name', '<', (utcdt + timedelta(hours=+24)).strftime(
                                      OE_DATETIMEFORMAT)),
                                  ('action', '=', 'sign_in'),
                                  '|', (
                                      'employee_id.department_id.id', '=', department_id),
                                  ('employee_id.saved_department_id.id', '=', department_id)
                                  ])

        unique_ids = []
        term_obj = self.pool.get('hr.employee.termination')
        data = att_obj.read(self.cr, self.uid, att_ids, ['employee_id'])
        for d in data:
            # if this employee's employment was terminated skip it
            term_ids = term_obj.search(
                self.cr, self.uid, [('name', '<=', self.date),
                                    ('employee_id.id', '=', d[
                                        'employee_id'][0]),
                                    ('state', 'not in', ['cancel'])])
            if len(term_ids) > 0:
                continue

            if d['employee_id'][0] not in unique_ids:
                unique_ids.append(d['employee_id'][0])

        return unique_ids

    def get_present(self, department_id):

        unique_ids = self.get_present_employees(department_id)

        onleave_ids = self.get_employees_on_leave(department_id, self.LVCODES)

        present_ids = [i for i in unique_ids if i not in onleave_ids]

        total = len(present_ids)
        self._present += total
        return total

    def get_employee_start_date(self, employee_id):

        first_day = False
        c_obj = self.pool.get('hr.contract')
        c_ids = c_obj.search(
            self.cr, self.uid, [('employee_id', '=', employee_id)])
        for contract in c_obj.browse(self.cr, self.uid, c_ids):
            if not first_day or contract.date_start < first_day:
                first_day = contract.date_start
        return first_day

    def get_absent(self, department_id):

        res = 0
        ee_leave_ids = self.get_employees_on_leave(department_id, self.LVCODES)

        ee_withsched_ids = []
        att_obj = self.pool.get('hr.attendance')
        sched_obj = self.pool.get('hr.schedule')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dt = datetime.strptime(self.date + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdt = (local_tz.localize(dt, is_dst=False)).astimezone(utc)
        sched_ids = sched_obj.search(
            self.cr, self.uid, [('date_start', '<=', self.date),
                                ('date_end', '>=', self.date),
                                '|', (
                                    'employee_id.department_id.id', '=', department_id),
                                ('employee_id.saved_department_id.id', '=', department_id)
                                ])
        for sched in sched_obj.browse(self.cr, self.uid, sched_ids):

            if sched.employee_id.id not in ee_withsched_ids:
                ee_withsched_ids.append(sched.employee_id.id)

            # skip if the employee is on leave
            if sched.employee_id.id in ee_leave_ids:
                continue

            # Skip if the employee wasn't hired yet
            hire_date = self.get_employee_start_date(sched.employee_id.id)
            if not hire_date or (datetime.strptime(hire_date, OE_DATEFORMAT).date() > dt.date()):
                continue

            rest_days = sched_obj.get_rest_days(
                self.cr, self.uid, sched.employee_id.id, dt)

            # if this is the employee's rest day skip it
            if dt.weekday() in rest_days:
                continue

            # if this employee's employment was terminated skip it
            term_ids = self.pool.get(
                'hr.employee.termination').search(self.cr, self.uid,
                                                  [('name', '<=', self.date),
                                                   ('employee_id.id', '=',
                                                    sched.employee_id.id),
                                                   ('state', 'not in', ['cancel'])])
            if len(term_ids) > 0:
                continue

            # Did the employee punch in that day?
            att_ids = att_obj.search(
                self.cr, self.uid, [(
                    'name', '>=', utcdt.strftime(OE_DATETIMEFORMAT)),
                    ('name', '<', (utcdt + timedelta(hours=+24)).strftime(
                        OE_DATETIMEFORMAT)),
                    ('action', '=', 'sign_in'),
                    ('employee_id.id', '=',
                     sched.employee_id.id),
                ])
            if len(att_ids) == 0:
                res += 1

        # Get employees who don't have a schedule
        ee_nosched_ids = self.pool.get('hr.employee').search(self.cr, self.uid,
                                                             ['|', ('department_id.id', '=', department_id),
                                                                   ('saved_department_id.id', '=', department_id),
                                                              ('id', 'not in', ee_withsched_ids)])
        for ee_id in ee_nosched_ids:

            # skip if the employee is on leave
            if ee_id in ee_leave_ids:
                continue

            # Skip if the employee wasn't hired yet
            hire_date = self.get_employee_start_date(ee_id)
            if not hire_date or (datetime.strptime(hire_date, OE_DATEFORMAT).date() > dt.date()):
                continue

            # if this employee's employment was terminated skip it
            term_ids = self.pool.get(
                'hr.employee.termination').search(self.cr, self.uid,
                                                  [('name', '<=', self.date),
                                                   ('employee_id.id', '=', ee_id),
                                                   ('state', 'not in', ['cancel'])])
            if len(term_ids) > 0:
                continue

            att_ids = att_obj.search(
                self.cr, self.uid, [(
                    'name', '>=', utcdt.strftime(OE_DATETIMEFORMAT)),
                    ('name', '<', (utcdt + timedelta(hours=+24)).strftime(
                        OE_DATETIMEFORMAT)),
                    ('action', '=', 'sign_in'),
                    ('employee_id.id', '=', ee_id),
                ])
            if len(att_ids) == 0:
                res += 1

        self._absent += res
        return (res and res or '-')

    def _on_leave(self, cr, uid, employee_id, d):

        leave_obj = self.pool.get('hr.holidays')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dtStart = datetime.strptime(
            d.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdtStart = (local_tz.localize(dtStart, is_dst=False)).astimezone(utc)
        utcdtNextStart = utcdtStart + timedelta(hours=+24)
        leave_ids = leave_obj.search(
            self.cr, self.uid, [('employee_id', '=', employee_id),
                                ('date_from', '<', utcdtNextStart.strftime(
                                    OE_DATETIMEFORMAT)),
                                ('date_to', '>=', utcdtStart.strftime(
                                    OE_DATETIMEFORMAT)),
                                ('type', '=', 'remove'),
                                ('state', 'in', [
                                    'validate', 'validate1']),
                                ])
        return (len(leave_ids) > 0)

    def get_restday(self, department_id):

        sched_obj = self.pool.get('hr.schedule')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dt = datetime.strptime(self.date + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdt = (local_tz.localize(dt, is_dst=False)).astimezone(utc)
        sched_ids = sched_obj.search(
            self.cr, self.uid, [('date_start', '<=', self.date),
                                ('date_end', '>=', self.date),
                                '|', (
                                    'employee_id.department_id.id', '=', department_id),
                                ('employee_id.saved_department_id.id', '=', department_id)
                                ])
        res = 0
        otr = 0     # restday OT
        for sched in sched_obj.browse(self.cr, self.uid, sched_ids):

            # If the employee is on leave, skip it
            if self._on_leave(self.cr, self.uid, sched.employee_id.id,
                              datetime.strptime(self.date, OE_DATEFORMAT).date()):
                continue

            rest_days = sched_obj.get_rest_days(
                self.cr, self.uid, sched.employee_id.id, dt)
            if dt.weekday() in rest_days:
                # Make sure the employee didn't punch in that day
                att_ids = self.pool.get(
                    'hr.attendance').search(self.cr, self.uid,
                                            [('name', '>=', utcdt.strftime(OE_DATETIMEFORMAT)),
                                             ('name', '<', (utcdt + timedelta(hours=+24)).strftime(
                                                 OE_DATETIMEFORMAT)),
                                             ('action', '=', 'sign_in'),
                                             ('employee_id.id', '=',
                                              sched.employee_id.id),
                                             ])
                if len(att_ids) == 0:
                    res += 1
                else:
                    otr += 1

        self._restday += res
        res_str = otr > 0 and str(res) + '(' + str(otr) + ')' or str(res)
        return ((res or otr) and res_str or '-')

    def _get_leave_ids(self, department_id, codes):

        if isinstance(codes, str):
            codes = [codes]

        leave_obj = self.pool.get('hr.holidays')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')
        dtStart = datetime.strptime(self.date + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdtStart = (local_tz.localize(dtStart, is_dst=False)).astimezone(utc)
        utcdtNextStart = utcdtStart + timedelta(hours=+24)
        leave_ids = leave_obj.search(
            self.cr, self.uid, [('holiday_status_id.code', 'in', codes),
                                ('date_from', '<', utcdtNextStart.strftime(
                                    OE_DATETIMEFORMAT)),
                                ('date_to', '>=', utcdtStart.strftime(
                                    OE_DATETIMEFORMAT)),
                                ('type', '=', 'remove'),
                                ('state', 'in', [
                                    'validate', 'validate1']),
                                '|', (
                                    'employee_id.department_id.id', '=', department_id),
                                ('employee_id.saved_department_id.id', '=', department_id)
                                ])
        return leave_ids

    def get_leave(self, department_id, codes):

        leave_ids = self._get_leave_ids(department_id, codes)
        res = len(leave_ids)
        return res

    def get_employees_on_leave(self, department_id, codes):

        leave_ids = self._get_leave_ids(department_id, codes)

        employee_ids = []
        data = self.pool.get('hr.holidays').read(
            self.cr, self.uid, leave_ids, ['employee_id'])
        for d in data:
            if d.get('employee_id', False) and d['employee_id'][0] not in employee_ids:
                employee_ids.append(d['employee_id'][0])

        return employee_ids

    def get_al(self, department_id):

        res = self.get_leave(department_id, 'LVANNUAL')
        self._al += res
        return (res and res or '-')

    def get_sl(self, department_id):

        res = self.get_leave(department_id, ['LVSICK', 'LVSICK50', 'LVSICK00'])
        self._sl += res
        return (res and res or '-')

    def get_ml(self, department_id):

        res = self.get_leave(department_id, 'LVMATERNITY')
        self._ml += res
        return (res and res or '-')

    def get_ol(self, department_id):

        codes = ['LVBEREAVEMENT', 'LVWEDDING',
                 'LVMMEDICAL', 'LVPTO', 'LVCIVIC']
        res = self.get_leave(department_id, codes)
        self._ol += res
        return (res and res or '-')

    def get_terminated(self, department_id):

        res = 0
        seen_ids = []
        term_obj = self.pool.get('hr.employee.termination')
        term_ids = term_obj.search(
            self.cr, self.uid, [('name', '=', self.date)])
        for term in term_obj.browse(self.cr, self.uid, term_ids):
            if term.employee_id.department_id:
                dept_id = term.employee_id.department_id.id
            elif term.employee_id.saved_department_id:
                dept_id = term.employee_id.saved_department_id.id
            else:
                dept_id = False
            if term.employee_id.id not in seen_ids and dept_id == department_id:
                res += 1
                seen_ids.append(term.employee_id.id)
        self._terminated += res
        return (res and res or '-')

    def get_sum_present(self):

        return self._present

    def get_sum_absent(self):

        return self._absent

    def get_sum_restday(self):

        return self._restday

    def get_sum_al(self):

        return self._al

    def get_sum_sl(self):

        return self._sl

    def get_sum_ml(self):

        return self._ml

    def get_sum_ol(self):

        return self._ol

    def get_sum_terminated(self):

        return self._terminated
