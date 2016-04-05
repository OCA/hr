# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp.exceptions import ValidationError


class TestHolidaysComputeDays(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysComputeDays, self).setUp()
        self.contract_model = self.env["hr.contract"]
        self.employee_model = self.env['hr.employee']
        self.holiday_status_model = self.env['hr.holidays.status']
        self.holiday_model = self.env['hr.holidays']
        self.public_holiday_model = self.env["hr.holidays.public"]
        self.public_holiday_model_line = self.env["hr.holidays.public.line"]
        self.employee_model = self.env['hr.employee']
        self.calendar_model = self.env['resource.calendar']
        self.calendar_attendance_model = (
            self.env['resource.calendar.attendance']
        )

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        # create calendar
        calendar = self.calendar_model.create({
            'name': 'Calendar'
        })
        for day in range(0, 5):
            self.calendar_attendance_model.create(
                {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '18',
                    'calendar_id': calendar.id
                }
            )

        # create contract
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '1990-10-14',
                'wage': 5000,
                'working_hours': calendar.id
            }
        )

        # Create public holidays
        public_holiday = self.public_holiday_model.create({
            'year': 1994,
        })
        self.public_holiday_model_line.create({
            'name': 'Public Holiday',
            'date': '1994-10-14',
            'year_id': public_holiday.id
        })

        # create leave types that we will be manupilating
        self.holiday_type = self.holiday_status_model.create(
            {
                'name': 'Leave',
                'exclude_public_holidays': True,
                'exclude_rest_days': True,
            }
        )

    def test_schedule_on_rest_day(self):
        # let's schedule start and then end date on a rest day
        with self.assertRaises(ValidationError):
            self.holiday_model.create({
                'name': 'Hol10',
                'employee_id': self.employee.id,
                'type': 'remove',
                'holiday_type': 'employee',
                'holiday_status_id': self.holiday_type.id,
                'date_from': '1994-10-01 00:10:00',
                'date_to': '1994-10-05 23:59:59',
            })

        with self.assertRaises(ValidationError):
            self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_type.id,
                'date_from': '1994-10-03 00:10:00',
                'date_to': '1994-10-05 23:59:59',
            })

    def test_schedule_on_public_holiday(self):
        # let's schedule start and then end date on public holiday
        with self.assertRaises(ValidationError):
            self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_type.id,
                'date_from': '1994-10-14 00:10:00',
                'date_to': '1994-10-15 23:59:59',
            })
        with self.assertRaises(ValidationError):
            self.holiday_model.create({
                'name': 'Hol10',
                'employee_id': self.employee.id,
                'type': 'remove',
                'holiday_type': 'employee',
                'holiday_status_id': self.holiday_type.id,
                'date_from': '1994-10-06 00:10:00',
                'date_to': '1994-10-14 23:59:59',
            })

    def test_leave_creation_ok(self):
        # let's schedule start and then end date on public holiday
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-11 00:10:00',
            'date_to': '1994-10-13 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertTrue(leave)

    def test_no_overlap(self):
        # leave overlaps no weekedn or public holiday
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-17 00:10:00',
            'date_to': '1994-10-21 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_overlap_weekend(self):
        # let's leave schedule overlap weekend
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-21 00:10:00',
            'date_to': '1994-10-27 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_overlap_holiday_and_rest_day(self):
        # let's leave schedule overlap weekend and restday
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 00:10:00',
            'date_to': '1994-10-19 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_overlap_for_non_conventional_rest_day(self):
        # let's leave schedule overlap on restday for non conventional restday
        # create calendar
        calendar = self.calendar_model.create({
            'name': 'Calendar'
        })
        for day in (2, 3, 4, 5, 6):
            self.calendar_attendance_model.create(
                {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '18',
                    'calendar_id': calendar.id
                }
            )
        # create contract
        self.contract.write(
            {
                'working_hours': calendar.id
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-17 00:10:00',
            'date_to': '1994-10-23 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_holiday_and_rest_day(self):
        # lwe have a holiday type that does not exclude public holiday or
        # rest day
        self.holiday_type.write(
            {
                'exclude_public_holidays': False,
                'exclude_rest_days': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 00:10:00',
            'date_to': '1994-10-17 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_holiday(self):
        # lwe have a holiday type that excludes on rest days
        self.holiday_type.write(
            {
                'exclude_public_holidays': False,
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 00:10:00',
            'date_to': '1994-10-18 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_rest_day(self):
        # lwe have a holiday type that does not exclude rest days
        self.holiday_type.write(
            {
                'exclude_rest_days': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 00:10:00',
            'date_to': '1994-10-17 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_schedule_holiday_and_rest_day(self):
        # let's run test assumign employee has not schedule
        self.contract.write(
            {
                'working_hours': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 00:10:00',
            'date_to': '1994-10-20 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_contract_holiday_and_rest_day(self):
        # let's run test assumign employee has not schedule
        self.contract.unlink()
        leave = self.holiday_model.new({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 00:10:00',
            'date_to': '1994-10-20 23:59:59',
        })
        leave.on_change_number_of_days()
        self.assertEqual(leave.number_of_days_temp, 5)
