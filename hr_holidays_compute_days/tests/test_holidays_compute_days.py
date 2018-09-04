# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestHolidaysComputeDaysBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHolidaysComputeDaysBase, cls).setUpClass()
        cls.HrHolidays = cls.env['hr.holidays']
        cls.calendar = cls.env['resource.calendar'].create({
            'name': 'Calendar',
        })
        for day in range(5):  # From monday to friday
            cls.calendar.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '12',
                }),
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '14',
                    'hour_to': '18',
                }),
            ]
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employee 1',
            'resource_calendar_id': cls.calendar.id,
        })
        cls.holiday_type = cls.env['hr.holidays.status'].create({
            'name': 'Leave Type Test',
            'exclude_rest_days': True,
            'compute_full_days': True,
        })
        cls.holiday_type_no_excludes = cls.env['hr.holidays.status'].create({
            'name': 'Leave Type Test Without excludes',
            'exclude_rest_days': False,
            'compute_full_days': False,
        })
        # Remove timezone for controlling data better
        cls.env.user.tz = False


class TestHolidaysComputeDays(TestHolidaysComputeDaysBase):
    def test_onchange_dates(self):
        holidays = self.HrHolidays.new({
            'date_from_full': '1946-12-20',
            'date_to_full': '1946-12-21',
            'from_full_day': True,
            'to_full_day': True,
        })
        holidays._onchange_date_from_full()
        self.assertEqual(holidays.date_from, '1946-12-20 00:00:00')
        holidays._onchange_date_to_full()
        self.assertEqual(holidays.date_to, '1946-12-21 23:59:59')

    def test_compute_dates(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-20 08:10:00',
            'date_to': '1946-12-21 15:45:30',
        })
        self.assertEqual(holidays.date_from_full, '1946-12-20')
        self.assertEqual(holidays.date_to_full, '1946-12-21')

    def test_number_days_excluding_full_day_employee(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-21 00:00:00',  # Saturday
            'date_to': '1946-12-27 11:00:00',  # Friday
            'holiday_status_id': self.holiday_type.id,
            'employee_id': self.employee.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 5.0)

    def test_number_days_not_excluding(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type_no_excludes.id,
            'employee_id': self.employee.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 7.0)
