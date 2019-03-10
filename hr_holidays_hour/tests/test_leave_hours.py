# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning as UserError


class TestLeaveHours(common.TransactionCase):
    def setUp(self):
        super(TestLeaveHours, self).setUp()

        Leave = self.env['hr.holidays']
        HolidaysStatus = self.env['hr.holidays.status']
        Employee = self.env['hr.employee']

        dt_holiday = datetime.today() + relativedelta(months=2)
        self.holiday_start = dt_holiday.replace(
            hour=8, minute=0, second=0, microsecond=0)
        self.holiday_end = dt_holiday.replace(
            hour=18, minute=0, second=0, microsecond=0)

        holiday_start = self.holiday_start.strftime(DF)
        holiday_end = self.holiday_end.strftime(DF)

        Calendar = self.env['resource.calendar']
        self.calendar = Calendar.create({
            'name': 'Calendar 1',
        })

        for i in range(0, 7):
            self.env['resource.calendar.attendance'].create({
                'name': 'Day ' + str(i),
                'dayofweek': str(i),
                'hour_from': 8.0,
                'hour_to': 16.0,
                'calendar_id': self.calendar.id,
            })

        self.employee_1 = Employee.create({
            'name': 'Employee 1',
            'calendar_id': self.calendar.id,
        })
        self.employee_2 = Employee.create({
            'name': 'Employee 2',
            'calendar_id': self.calendar.id,
        })
        self.employee_3 = Employee.create({
            'name': 'Employee 3',
        })
        self.employee_4 = Employee.create({
            'name': 'Failing Employee',
            'calendar_id': self.calendar.id,
        })

        self.contract_1 = self.env['hr.contract'].create({
            'name': 'Contract 1',
            'employee_id': self.employee_3.id,
            'wage': 2000.0,
            'working_hours': self.calendar.id,
        })

        self.status_1 = HolidaysStatus.create({
            'name': 'Status 1',
            'limit': True,
        })
        self.status_2 = HolidaysStatus.create({
            'name': 'Status 2',
            'limit': False,
        })

        self.leave_allocation_1 = Leave.create({
            'name': 'Allocation Request 1',
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_1.id,
            'number_of_days_temp': 10,
            'number_of_hours_temp': 80,
            'type': 'add',
        })

        self.leave_1 = Leave.create({
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'type': 'remove',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_1.id,
            'number_of_hours_temp': 8,
        })

        self.leave_allocation_2 = Leave.create({
            'name': 'Allocation Request 2',
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_2.id,
            'number_of_days_temp': 10,
            'type': 'add',
        })

        self.leave_2 = Leave.create({
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'type': 'remove',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_2.id,
        })

        self.leave_allocation_3 = Leave.create({
            'name': 'Allocation Request 3',
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_3.id,
            'number_of_days_temp': 10,
            'type': 'add',
        })

        self.leave_3 = Leave.create({
            'holiday_status_id': self.status_1.id,
            'holiday_type': 'employee',
            'type': 'remove',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_3.id,
        })

    def test_01_onchange(self):

        def test_onchange(leave, employee, allocation):
            field_onchange = leave._onchange_spec()
            self.assertEqual(field_onchange.get('employee_id'), '1')
            self.assertEqual(field_onchange.get('date_from'), '1')
            self.assertEqual(field_onchange.get('date_to'), '1')

            values = {
                'employee_id': employee.id,
                'date_from': self.holiday_start.strftime(DF),
                'date_to': self.holiday_end.strftime(DF),
            }
            if allocation:
                leave.with_context(default_type='add').onchange(
                    values, 'employee_id', field_onchange)
                leave.with_context(default_type='add').onchange(
                    values, 'date_from', field_onchange)
                leave.with_context(default_type='add').onchange(
                    values, 'date_to', field_onchange)
            else:
                leave.onchange(values, 'employee_id', field_onchange)
                leave.onchange(values, 'date_from', field_onchange)
                leave.onchange(values, 'date_to', field_onchange)

        test_list = [
            {
                'leave': self.leave_1,
                'employee': self.employee_1,
                'allocation': False,
            },
            {
                'leave': self.leave_2,
                'employee': self.employee_2,
                'allocation': False,
            },
            {
                'leave': self.leave_3,
                'employee': self.employee_3,
                'allocation': False,
            },
            {
                'leave': self.leave_allocation_1,
                'employee': self.employee_1,
                'allocation': True,
            },
            {
                'leave': self.leave_allocation_2,
                'employee': self.employee_2,
                'allocation': True,
            },
            {
                'leave': self.leave_allocation_3,
                'employee': self.employee_3,
                'allocation': True,
            },
        ]

        for test in test_list:
            test_onchange(test['leave'], test['employee'], test['allocation'])

    def test_02_onchange_fail(self):
        field_onchange = self.leave_1._onchange_spec()
        values = {
            'date_from': self.holiday_end.strftime(DF),
            'date_to': self.holiday_start.strftime(DF),
        }

        with self.assertRaises(UserError):
            self.leave_1.onchange(values, 'date_from', field_onchange)
        with self.assertRaises(UserError):
            self.leave_1.onchange(values, 'date_to', field_onchange)

        values.update({
            'employee_id': None,
            'date_from': self.holiday_start.strftime(DF),
            'date_to': self.holiday_end.strftime(DF),
        })

        self.leave_1.onchange(values, 'employee_id', field_onchange)

        with self.assertRaises(UserError):
            self.leave_1.onchange(values, 'date_from', field_onchange)
        with self.assertRaises(UserError):
            self.leave_1.onchange(values, 'date_to', field_onchange)

    def test_03_creation_fail(self):
        with self.assertRaises(ValidationError):
            self.env['hr.holidays'].create({
                'holiday_status_id': self.status_2.id,
                'holiday_type': 'employee',
                'type': 'remove',
                'date_from': self.holiday_start.strftime(DF),
                'date_to': self.holiday_end.strftime(DF),
                'employee_id': self.employee_4.id,
                'number_of_hours_temp': 8.0
            })

    def test_04_get_work_limits(self):

        Calendar = self.env['resource.calendar']
        start_dt, work_limits = Calendar._get_work_limits(
            self.holiday_end, self.holiday_start)
        self.assertEqual(start_dt, self.holiday_start)
        self.assertEqual(work_limits, [
            (
                self.holiday_start.replace(
                    hour=0, minute=0, second=0, microsecond=0),
                self.holiday_start
            ),
            (
                self.holiday_end,
                self.holiday_end.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            ),
        ])

        start_dt, work_limits = Calendar._get_work_limits(
            self.holiday_end, None)
        self.assertEqual(start_dt, self.holiday_end.replace(
            hour=0, minute=0, second=0, microsecond=0))
        self.assertEqual(work_limits, [
            (
                self.holiday_end,
                self.holiday_end.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            ),
        ])

        start_dt, work_limits = Calendar._get_work_limits(
            None, self.holiday_start)
        self.assertEqual(start_dt, self.holiday_start)
        self.assertEqual(work_limits, [
            (
                self.holiday_start.replace(
                    hour=0, minute=0, second=0, microsecond=0),
                self.holiday_start
            ),
        ])

        start_dt, work_limits = Calendar._get_work_limits(None, None)
        self.assertEqual(start_dt, datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0))
        self.assertEqual(work_limits, [])

    def test_05_get_working_intervals_of_day(self):
        default_interval = (
            self.holiday_start.hour,
            self.holiday_end.hour
        )
        Calendar = self.env['resource.calendar']
        interval = Calendar.get_working_intervals_of_day(
            self.holiday_start,
            self.holiday_end,
            default_interval=default_interval
        )

        self.assertEqual(interval, [(
            self.holiday_start,
            self.holiday_end
        )])

    def test_06_compute_leaves_count(self):
        employee_list = self.employee_1 + \
            self.employee_2 + \
            self.employee_3 + \
            self.employee_4
        employee_list._compute_leaves_count()

    def test_07_get_hours(self):
        self.leave_allocation_1.action_approve()
        self.leave_1.action_approve()
        hours = self.status_1.get_hours(self.employee_1)

        self.assertEqual(hours['virtual_remaining_hours'], 72.0)
        self.assertEqual(hours['remaining_hours'], 72.0)
        self.assertEqual(hours['hours_taken'], 8.0)
        self.assertEqual(hours['max_hours'], 80.0)

        self.assertEqual(self.status_1.with_context(
            employee_id=self.employee_1.id).virtual_remaining_hours, 72.0)
        self.assertEqual(self.status_1.with_context(
            employee_id=self.employee_1.id).remaining_hours, 72.0)
        self.assertEqual(self.status_1.with_context(
            employee_id=self.employee_1.id).hours_taken, 8.0)
        self.assertEqual(self.status_1.with_context(
            employee_id=self.employee_1.id).max_hours, 80.0)

        self.assertEqual(self.status_1.max_hours, 0.0)

        self.assertEqual(
            self.status_1.with_context(
                employee_id=self.employee_1.id).name_get(),
            [(self.status_1.id, 'Status 1')])

        self.assertEqual(
            self.status_2.with_context(
                employee_id=self.employee_1.id).name_get(),
            [(self.status_2.id, 'Status 2  (0.0 Left)')])

        self.assertEqual(
            self.status_1.name_get(),
            [(self.status_1.id, 'Status 1')])
