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

        # Create 2 employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        self.employee2 = self.employee_model.create({
            'name': 'Employee 2',
        })

        # create calendar
        calendar = self.calendar_model.create({
            'name': 'Calendar'
        })
        for day in range(5):
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

        self.contract2 = self.contract_model.create(
            {
                'employee_id': self.employee2.id,
                'name': 'Contract 2',
                'date_start': '1990-10-01',
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
        self.public_holiday_model_line.create({
            'name': 'Public Holiday2',
            'date': '1994-10-28',
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

        self.holiday_type_no_excludes = self.holiday_status_model.create(
            {
                'name': 'Leave Without excludes',
                'exclude_public_holidays': False,
                'exclude_rest_days': False,
            }
        )

    def test_schedule_on_rest_day(self):
        # let's schedule start and then end date on a rest day
        with self.assertRaises(ValidationError):
            leave = self.holiday_model.create(
                {
                    'name': 'Hol10',
                    'employee_id': self.employee.id,
                    'type': 'remove',
                    'holiday_type': 'employee',
                    'holiday_status_id': self.holiday_type.id,
                    'date_from': '1994-10-01 08:00:00',
                    'date_to': '1994-10-05 18:00:00',
                })
            leave._onchange_date_from()

        with self.assertRaises(ValidationError):
            leave = self.holiday_model.create(
                {
                    'name': 'Hol11',
                    'type': 'remove',
                    'holiday_type': 'employee',
                    'employee_id': self.employee.id,
                    'holiday_status_id': self.holiday_type.id,
                    'date_from': '1994-10-03 08:00:00',
                    'date_to': '1994-10-08 18:00:00',
                })
            leave._onchange_date_to()

    def test_schedule_on_public_holiday(self):
        # let's schedule start and then end date on public holiday
        with self.assertRaises(ValidationError):
            leave = self.holiday_model.create(
                {
                    'name': 'Hol12',
                    'type': 'remove',
                    'holiday_type': 'employee',
                    'employee_id': self.employee.id,
                    'holiday_status_id': self.holiday_type.id,
                    'date_from': '1994-10-14 08:00:00',
                    'date_to': '1994-10-17 18:00:00',
                })
            leave._onchange_date_from()
        with self.assertRaises(ValidationError):
            leave = self.holiday_model.create(
                {
                    'name': 'Hol13',
                    'employee_id': self.employee.id,
                    'type': 'remove',
                    'holiday_type': 'employee',
                    'holiday_status_id': self.holiday_type.id,
                    'date_from': '1994-10-06 08:00:00',
                    'date_to': '1994-10-14 18:00:00',
                })
            leave._onchange_date_to()
        with self.assertRaises(ValidationError):
            leave = self.holiday_model.create(
                {
                    'name': 'Hol13',
                    'employee_id': self.employee.id,
                    'type': 'remove',
                    'holiday_type': 'employee',
                    'holiday_status_id': self.holiday_type.id,
                    'date_from': '1994-10-25 08:00:00',
                    'date_to': '1994-10-28 18:00:00',
                })
            leave._onchange_employee(self.employee2.id)

    def test_leave_creation_ok(self):
        # let's schedule holiday with date_from and date to in working days
        leave = self.holiday_model.new({
            'name': 'Hol14',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-11 08:00:00',
            'date_to': '1994-10-13 18:00:00',
        })
        leave._onchange_date_from()
        self.assertTrue(leave)

    def test_no_overlap(self):
        # leave overlaps no weekend or public holiday
        leave = self.holiday_model.new({
            'name': 'Hol15',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-17 08:00:00',
            'date_to': '1994-10-21 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_overlap_weekend(self):
        # let's leave schedule overlap weekend
        leave = self.holiday_model.new({
            'name': 'Hol16',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-21 08:00:00',
            'date_to': '1994-10-27 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_overlap_holiday_and_rest_day(self):
        # let's leave schedule overlap weekend and public holiday
        leave = self.holiday_model.new({
            'name': 'Hol17',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 08:00:00',
            'date_to': '1994-10-19 18:00:00',
        })
        leave._onchange_date_from()
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
                    'calendar_id': calendar[0].id
                }
            )
        # create contract
        self.contract.write(
            {
                'working_hours': calendar[0].id
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol18',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-16 08:00:00',
            'date_to': '1994-10-22 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_holiday_and_rest_day(self):
        # we have a holiday type that does not exclude public holiday or
        # rest day
        self.holiday_type.write(
            {
                'exclude_public_holidays': False,
                'exclude_rest_days': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol19',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 08:00:00',
            'date_to': '1994-10-17 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_holiday(self):
        # lwe have a holiday type that excludes on rest days
        self.holiday_type.write(
            {
                'exclude_public_holidays': False,
                'exclude_rest_days': True
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol20',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 08:00:00',
            'date_to': '1994-10-18 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_exclude_rest_day(self):
        # lwe have a holiday type that does not exclude rest days
        self.holiday_type.write(
            {
                'exclude_public_holidays': True,
                'exclude_rest_days': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol21',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-12 08:00:00',
            'date_to': '1994-10-17 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_schedule_holiday_and_rest_day(self):
        # let's run test assumign employee has not schedule
        self.contract.write(
            {
                'working_hours': False
            }
        )
        leave = self.holiday_model.new({
            'name': 'Hol22',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 08:00:00',
            'date_to': '1994-10-20 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_no_contract_holiday_and_rest_day(self):
        # let's run test assumign employee has not schedule
        self.contract.unlink()
        leave = self.holiday_model.new({
            'name': 'Hol23',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 08:00:00',
            'date_to': '1994-10-20 18:00:00',
        })
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 5)

    def test_onchange_employee(self):
        # let's run test assumign employee has not schedule
        self.contract.unlink()
        vals = {
            'name': 'Hol23',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type.id,
            'date_from': '1994-10-13 08:00:00',
            'date_to': '1994-10-20 18:00:00',
        }
        leave = self.holiday_model.new(vals)
        vals = vals.copy()
        vals.update({
            'employee_id': self.employee2.id,
            # set to zero to force onchange return new value
            'number_of_days_temp': 0,
        })
        res = leave.onchange(vals,
                             'employee_id',
                             {'employee_id': '1'})
        self.assertEqual(res['value']['number_of_days_temp'], 5)

    def test_onchange_holiday_status(self):
        # we have a holiday type that does not exclude public holiday or
        # rest day
        vals = {
            'name': 'Hol24',
            'employee_id': self.employee.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_type_no_excludes.id,
            'date_from': '1994-10-13 08:00:00',
            'date_to': '1994-10-20 18:00:00',
        }
        leave = self.holiday_model.new(vals)
        leave._onchange_date_from()
        self.assertEqual(leave.number_of_days_temp, 8)

        # now switch to holiday type with excludes
        vals = vals.copy()
        vals.update({
            'holiday_status_id': self.holiday_type.id,
            # set to zero to force onchange return new value
            'number_of_days_temp': 0,
        })
        res = leave.onchange(vals,
                             'holiday_status_id',
                             {'holiday_status_id': '1'})
        self.assertEqual(res['value']['number_of_days_temp'], 5)
