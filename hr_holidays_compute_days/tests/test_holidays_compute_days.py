# -*- coding: utf-8 -*-
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
        cls.HrHolidaysPublic = cls.env["hr.holidays.public"]
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
        # Calendar for an FTE of 80/100 with presence Monday and Friday AM only
        cls.calendar_FTE_80 = cls.env['resource.calendar'].create({
            'name': 'Calendar FTE 80/100',
        })
        for day in ['1','2','3']:  # From Tuesday to Thursday (8H)
            cls.calendar_FTE_80.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '12',
                }),
                (0, 0, {
                    'name': 'Attendance All Day',
                    'dayofweek': str(day),
                    'hour_from': '14',
                    'hour_to': '18',
                }),
            ]
        for day in ['0', '4']:  # monday to wednesday (4H)
            cls.calendar_FTE_80.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance AM only',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '12',
                }),
            ]
        cls.address_1 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.uk').id,
        })
        cls.address_2 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.es').id,
            'state_id': cls.env.ref('base.state_es_cr').id,
        })
        cls.address_be = cls.env['res.partner'].create({
            'name': 'Address (Belgium)',
            'country_id': cls.env.ref('base.be').id,
        })
        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'Employee 1',
            'calendar_id': cls.calendar.id,
            'address_id': cls.address_1.id,
        })
        cls.employee_2 = cls.env['hr.employee'].create({
            'name': 'Employee 2',
            'calendar_id': cls.calendar.id,
            'address_id': cls.address_2.id,
        })
        cls.employee_be = cls.env['hr.employee'].create({
            'name': 'Employee (Belgium)',
            'calendar_id': cls.calendar_FTE_80.id,
            'address_id': cls.address_be.id,
        })
        # Use a very old year for avoiding to collapse with current data
        cls.public_holiday_global = cls.HrHolidaysPublic.create({
            'year': 1946,
            'line_ids': [
                (0, 0, {
                    'name': 'Christmas',
                    'date': '1946-12-25',
                }),
            ],
        })
        cls.public_holiday_country = cls.HrHolidaysPublic.create({
            'year': 1946,
            'country_id': cls.address_2.country_id.id,
            'line_ids': [
                (0, 0, {
                    'name': 'Before Christmas',
                    'date': '1946-12-24',
                }),
                (0, 0, {
                    'name': 'Even More Before Christmas',
                    'date': '1946-12-23',
                    'state_ids': [
                        (6, 0, cls.address_2.state_id.ids),
                    ]
                }),
            ],
        })
        cls.holiday_type = cls.env['hr.holidays.status'].create({
            'name': 'Leave Type Test',
            'exclude_public_holidays': True,
            'exclude_rest_days': True,
            'compute_full_days': True,
        })
        cls.holiday_type_no_excludes = cls.env['hr.holidays.status'].create({
            'name': 'Leave Type Test Without excludes',
            'exclude_public_holidays': False,
            'exclude_rest_days': False,
            'compute_full_days': False,
        })
        cls.holiday_type_hours = cls.env['hr.holidays.status'].create({
            'name': 'Leave Type Test',
            'exclude_public_holidays': True,
            'exclude_rest_days': True,
            'compute_full_days': False,
        })
        # In Odoo, date values are always displayed to the user according to the BROWSER timezone
        # While on the other hand many parts of the code does convert dates according to
        # user's preference (cls.env.user.tz)
        # A mismatch between browser's and user's timezone lead to wrong behavior
        # See also https://github.com/odoo/odoo/issues/28518
        # Here we set timezone to 'GB' (corresponding to browser's timezone in unit-test mode)
        cls.env.user.tz = 'GB'

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

    def test_number_days_excluding_employee_1(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type.id,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 4)

    def _test_number_days_excluding_employee_2(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type.id,
            'employee_id': self.employee_2.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 2)

    def test_number_days_not_excluding(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type_no_excludes.id,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 7)

    def test_number_days_without_calendar(self):
        self.employee_1.calendar_id = False
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type_no_excludes.id,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0)

    def test_fractional_number_days(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 00:00:00',
            'date_to': '1946-12-23 14:00:00',
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0.5)

    def test_fractional_number_days_time_off(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-24 07:00:00',
            'date_to': '1946-12-24 08:00:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_be.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0)

    def test_fractional_number_days_am(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 08:00:00',
            'date_to': '1946-12-23 14:00:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0.5)

    def test_fractional_number_days_pm(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 12:00:00',
            'date_to': '1946-12-23 16:00:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0.25)

    def test_fractional_number_days_1H(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 14:00:00',
            'date_to': '1946-12-23 15:00:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0.125)

    def test_fractional_number_days_35MIN(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 15:00:00',
            'date_to': '1946-12-23 15:35:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_1.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 0.0729)

    # Employee with 80% FTE (monday/friday AM only), one public day 25/12 (Wednesday)
    # From 23/12 08:00 to 31/12 10:00
    # Holiday type compute full days = False
    # Should compute 0.5 + 1 + 0 + 1 + 0.5 + 0 + 0 + 0.5 + 0.25 =   3.75
    def test_fractional_number_days_FTE_80(self):
        holidays = self.HrHolidays.new({
            'date_from': '1946-12-23 08:00:00',
            'date_to': '1946-12-31 10:00:00',
            'holiday_status_id': self.holiday_type_hours,
            'employee_id': self.employee_be.id,
        })
        holidays._onchange_data_hr_holidays_compute_days()
        self.assertEqual(holidays.number_of_days_temp, 3.75)
