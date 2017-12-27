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
        cls.address_1 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.uk').id,
        })
        cls.address_2 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.es').id,
            'state_id': cls.env.ref('base.state_es_cr').id,
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
