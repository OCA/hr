# ©  2018 Fekete Mihai <feketemihai@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models


class HrHolidaySummaryReport(models.AbstractModel):
    _inherit = 'report.hr_holidays.report_holidayssummary'

    def _get_leaves_summary(self, start_date, empid, holiday_type):
        res = []
        count = 0
        count_hours = 0
        start_date = fields.Date.from_string(start_date)
        end_date = start_date + relativedelta(days=59)
        for index in range(0, 60):
            current = start_date + timedelta(index)
            res.append({'day': current.day, 'color': ''})
            if self._date_is_day_off(current):
                res[index]['color'] = '#ababab'
        # count and get leave summary details.
        if holiday_type == 'both':
            holiday_type = ['confirm', 'validate']
        elif holiday_type == 'Confirmed':
            holiday_type = ['confirm']
        else:
            holiday_type = ['validate']
        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', empid), ('state', 'in', holiday_type),
            ('type', '=', 'remove'), ('date_from', '<=', str(end_date)),
            ('date_to', '>=', str(start_date))
        ])
        for holiday in holidays:
            # Convert date to user timezone, otherwise the report will not be
            # consistent with the value displayed in the interface.
            date_from = fields.Datetime.from_string(holiday.date_from)
            date_from = fields.Datetime.context_timestamp(
                holiday, date_from).date()
            date_to = fields.Datetime.from_string(holiday.date_to)
            date_to = fields.Datetime.context_timestamp(
                holiday, date_to).date()
            for index in range(0, ((date_to - date_from).days + 1)):
                if date_from >= start_date and date_from <= end_date:
                    res[(date_from-start_date).days]['color'] = \
                        holiday.holiday_status_id.color_name
                date_from += timedelta(1)
            count += abs(holiday.number_of_days)
            count_hours += abs(holiday.number_of_hours)
        self.sum = count
        self.sum_hours = count_hours
        return res

    def _get_data_from_report(self, data):
        res = []
        employees = self.env['hr.employee']
        if 'depts' in data:
            for department in self.env['hr.department'].browse(data['depts']):
                res.append({'dept': department.name,
                            'data': [],
                            'color': self._get_day(data['date_from'])})
                for emp in employees.search([('department_id',
                                              '=',
                                              department.id)]):
                    res[len(res)-1]['data'].append({
                        'emp': emp.name,
                        'display': self._get_leaves_summary(
                            data['date_from'], emp.id, data['holiday_type']),
                        'sum': self.sum,
                        'sum_hours': self.sum_hours
                    })
        elif 'emp' in data:
            res.append({'data': []})
            for emp in employees.browse(data['emp']):
                res[0]['data'].append({
                    'emp': emp.name,
                    'display': self._get_leaves_summary(
                        data['date_from'], emp.id, data['holiday_type']),
                    'sum': self.sum,
                    'sum_hours': self.sum_hours
                })
        return res
