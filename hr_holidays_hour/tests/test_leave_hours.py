# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.tests import common


class TestLeaveHours(common.TransactionCase):
    def setUp(self):
        super().setUp()

        dt_holiday = datetime.today() + relativedelta(months=2)
        self.holiday_start = dt_holiday.replace(
            hour=8, minute=0, second=0, microsecond=0)
        self.holiday_end = dt_holiday.replace(
            hour=18, minute=0, second=0, microsecond=0)

        holiday_start = self.holiday_start
        holiday_end = self.holiday_end

        self.calendar = self.env['resource.calendar'].create({
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

        self.employee_1 = self.env['hr.employee'].create({
            'name': 'Employee 1',
            'resource_calendar_id': self.calendar.id,
        })
        self.employee_2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
            'resource_calendar_id': self.calendar.id,
        })
        self.employee_3 = self.env['hr.employee'].create({
            'name': 'Employee 3',
        })
        self.employee_4 = self.env['hr.employee'].create({
            'name': 'Failing Employee',
            'resource_calendar_id': self.calendar.id,
        })

        self.leave_type_1 = self.env['hr.leave.type'].create({
            'name': 'Leave Type 1',
            'allocation_type': 'no',
            'request_unit': 'hour',
        })
        self.leave_type_2 = self.env['hr.leave.type'].create({
            'name': 'Leave Type 2',
            'allocation_type': 'fixed',
            'request_unit': 'hour',
        })

        self.leave_allocation_1 = self.env['hr.leave.allocation'].create({
            'name': 'Allocation Request 1',
            'holiday_status_id': self.leave_type_1.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_1.id,
            'number_of_days': 10,
        })
        self.leave_allocation_1.action_approve()

        self.leave_1 = self.env['hr.leave'].create({
            'holiday_status_id': self.leave_type_1.id,
            'holiday_type': 'employee',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_1.id,
        })

        self.leave_allocation_2 = self.env['hr.leave.allocation'].create({
            'name': 'Allocation Request 2',
            'holiday_status_id': self.leave_type_2.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_2.id,
            'number_of_days': 10,
        })
        self.leave_allocation_2.action_approve()

        self.leave_2 = self.env['hr.leave'].create({
            'holiday_status_id': self.leave_type_2.id,
            'holiday_type': 'employee',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_2.id,
        })

        self.leave_allocation_3 = self.env['hr.leave.allocation'].create({
            'name': 'Allocation Request 3',
            'holiday_status_id': self.leave_type_2.id,
            'holiday_type': 'employee',
            'employee_id': self.employee_3.id,
            'number_of_days': 10,
        })
        self.leave_allocation_3.action_approve()

        self.leave_3 = self.env['hr.leave'].create({
            'holiday_status_id': self.leave_type_2.id,
            'holiday_type': 'employee',
            'date_from': holiday_start,
            'date_to': holiday_end,
            'employee_id': self.employee_3.id,
        })

    def test_compute_leaves_count(self):
        employees = self.employee_1 + \
            self.employee_2 + \
            self.employee_3 + \
            self.employee_4
        employees._compute_leaves_count()

    def test_remaining_leaves(self):
        self.assertEqual(self.employee_1.remaining_leaves, 0.0)
        self.assertEqual(self.employee_2.remaining_leaves, 80.0)
        self.assertEqual(self.employee_3.remaining_leaves, 80.0)
        self.assertEqual(self.employee_4.remaining_leaves, 0.0)
