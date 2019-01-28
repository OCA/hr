# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from pytz import timezone, UTC
from datetime import datetime, date

from odoo import fields

from odoo.tests import common


class TestHrHolidaysLeaveRequestWizard(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.today = fields.Date.today()
        self.main_company = self.env.ref('base.main_company')
        self.group_user = self.env.ref('base.group_user')
        self.User = self.env['res.users']
        self.SudoUser = self.User.sudo()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.LeaveType = self.env['hr.leave.type']
        self.SudoLeaveType = self.LeaveType.sudo()
        self.LeaveAllocation = self.env['hr.leave.allocation']
        self.SudoLeaveAllocation = self.LeaveAllocation.sudo()
        self.Leave = self.env['hr.leave']
        self.SudoLeave = self.Leave.sudo()
        self.Wizard = self.env['hr.leave.wizard']

    def test_2(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #2',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #2',
            'login': 'user_2',
            'email': 'user_2@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
            'user_id': user.id,
        })
        leave = self.SudoLeave.with_context({
            'default_user_id': user.id,
            'default_date_from': self.now,
            'default_date_to': self.now,
        }).create({
            'name': 'Leave #2',
            'holiday_status_id': leave_type.id,
            'employee_id': employee.id,
        })

        self.assertNotEqual(leave.date_from, leave.date_to)

    def test_3(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #3',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #3',
            'login': 'user_3',
            'email': 'user_3@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #3',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })
        tz = timezone(user.tz or 'UTC')
        date_from = tz.localize(datetime(
            2019, 1, 28, 10
        )).astimezone(UTC).replace(tzinfo=None)
        date_to = tz.localize(datetime(
            2019, 2, 3, 19
        )).astimezone(UTC).replace(tzinfo=None)
        leave = self.Leave.sudo(user.id).with_context({
            'default_user_id': user.id,
            'default_date_from': date_from,
            'default_date_to': date_to,
        }).create({
            'name': 'Leave #3',
            'holiday_status_id': leave_type.id,
            'employee_id': employee.id,
        })
        leave._onchange_leave_dates()

        self.assertEqual(leave.date_from, date_from)
        self.assertEqual(leave.date_to, date_to)
        self.assertEqual(leave.number_of_days, 4.625)

    def test_4(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #4',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #4',
            'login': 'user_4',
            'email': 'user_4@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
            'tz': 'Europe/Tallinn',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #4',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })
        tz = timezone(user.tz or 'UTC')
        date_from = tz.localize(datetime(
            2019, 1, 28, 7
        )).astimezone(UTC).replace(tzinfo=None)
        date_to = tz.localize(datetime(
            2019, 2, 3, 19
        )).astimezone(UTC).replace(tzinfo=None)
        leave = self.Leave.sudo(user.id).with_context({
            'default_user_id': user.id,
            'default_date_from': date_from,
            'default_date_to': date_to,
        }).create({
            'name': 'Leave #4',
            'holiday_status_id': leave_type.id,
            'employee_id': employee.id,
        })
        leave._onchange_leave_dates()

        self.assertEqual(
            leave.date_from,
            tz.localize(datetime(
                2019, 1, 28, 8
            )).astimezone(UTC).replace(tzinfo=None)
        )
        self.assertEqual(
            leave.date_to,
            tz.localize(datetime(
                2019, 2, 1, 17
            )).astimezone(UTC).replace(tzinfo=None)
        )
        self.assertEqual(leave.number_of_days, 5.0)

    def test_5(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #5',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #5',
            'login': 'user_5',
            'email': 'user_5@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #5',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })
        tz = timezone(self.env.user.tz or 'UTC')
        date_from = tz.localize(datetime(
            2019, 1, 28, 7
        )).astimezone(UTC).replace(tzinfo=None)
        date_to = tz.localize(datetime(
            2019, 2, 3, 19
        )).astimezone(UTC).replace(tzinfo=None)
        leave = self.Leave.with_context({
            'default_employee_id': employee.id,
            'default_date_from': date_from,
            'default_date_to': date_to,
        }).create({
            'name': 'Leave #5',
            'holiday_status_id': leave_type.id,
        })
        leave._onchange_leave_dates()

        self.assertEqual(
            leave.date_from,
            tz.localize(datetime(
                2019, 1, 28, 8
            )).astimezone(UTC).replace(tzinfo=None)
        )
        self.assertEqual(
            leave.date_to,
            tz.localize(datetime(
                2019, 2, 1, 17
            )).astimezone(UTC).replace(tzinfo=None)
        )
        self.assertEqual(leave.number_of_days, 5.0)

    def test_6(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #6',
            'allocation_type': 'fixed',
            'validity_start': False,
            'request_unit': 'day',
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #6',
            'login': 'user_6',
            'email': 'user_6@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #6',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })

        wizard = self.Wizard.create({
            'name': 'test_6',
            'employee_id': employee.id,
            'leave_type_id': leave_type.id,
            'date_from': date(2019, 4, 1),
            'date_to': date(2019, 4, 7),
        })
        wizard._onchange_employee_id()
        wizard._onchange_leave_type_id()
        self.assertEqual(len(wizard.day_ids), 7)
        self.assertEqual(len(wizard.interval_ids), 10)
        wizard.day_ids._compute_name()
        wizard.interval_ids._compute_name()

        day_0 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 1)
        )
        day_0.requested_days = 0.0
        day_0._onchange_requested_days()
        self.assertEqual(day_0.requested_days, 0.0)

        day_1 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 2)
        )
        day_1.requested_days = 0.49
        day_1._onchange_requested_days()
        self.assertEqual(day_1.requested_days, 0.5)

        day_2 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 3)
        )
        day_2.requested_days = 2.0
        day_2._onchange_requested_days()
        self.assertEqual(day_2.requested_days, 1.0)

        day_3 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 4)
        )
        day_3.requested_days = 0.5
        day_3._onchange_requested_days()
        self.assertEqual(day_3.requested_days, 0.5)

        day_4 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 5)
        )
        day_4.requested_days = 1.0
        day_4._onchange_requested_days()
        self.assertEqual(day_4.requested_days, 1.0)

        leaves = wizard.generate_leaves()
        self.assertEqual(len(leaves), 3)

        leave_1 = leaves.filtered(
            lambda leave: leave.name == 'test_6 (1/3)'
        )
        self.assertTrue(leave_1)
        self.assertEqual(leave_1.number_of_days, 0.5)

        leave_2 = leaves.filtered(
            lambda leave: leave.name == 'test_6 (2/3)'
        )
        self.assertTrue(leave_2)
        self.assertEqual(leave_2.number_of_days, 1.5)

        leave_3 = leaves.filtered(
            lambda leave: leave.name == 'test_6 (3/3)'
        )
        self.assertTrue(leave_3)
        self.assertEqual(leave_3.number_of_days, 1.0)

    def test_7(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #7',
            'allocation_type': 'fixed',
            'validity_start': False,
            'request_unit': 'hour',
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #7',
            'login': 'user_7',
            'email': 'user_7@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #7',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })

        wizard = self.Wizard.create({
            'name': 'test_7',
            'employee_id': employee.id,
            'leave_type_id': leave_type.id,
            'date_from': date(2019, 4, 1),
            'date_to': date(2019, 4, 7),
        })
        wizard._onchange_employee_id()
        wizard._onchange_leave_type_id()
        self.assertEqual(len(wizard.day_ids), 7)
        self.assertEqual(len(wizard.interval_ids), 10)
        wizard.day_ids._compute_name()
        wizard.interval_ids._compute_name()

        day_0 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 1)
        )
        day_0.interval_ids[0].requested_hours = 0.0
        day_0.interval_ids[0]._onchange_requested_hours()
        self.assertEqual(day_0.interval_ids[0].requested_hours, 0.0)
        day_0.interval_ids[1].requested_hours = 0.0
        day_0.interval_ids[1]._onchange_requested_hours()
        self.assertEqual(day_0.interval_ids[1].requested_hours, 0.0)

        day_1 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 2)
        )
        day_1.interval_ids[0].requested_hours = 3.9
        day_1.interval_ids[0]._onchange_requested_hours()
        self.assertEqual(day_1.interval_ids[0].requested_hours, 4.0)
        day_1.interval_ids[1].requested_hours = 0.0
        day_1.interval_ids[1]._onchange_requested_hours()
        self.assertEqual(day_1.interval_ids[1].requested_hours, 0.0)

        day_2 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 3)
        )
        day_2.interval_ids[0].requested_hours = 8.0
        day_2.interval_ids[0]._onchange_requested_hours()
        self.assertEqual(day_2.interval_ids[0].requested_hours, 4.0)
        day_2.interval_ids[1].requested_hours = 4.0
        day_2.interval_ids[1]._onchange_requested_hours()
        self.assertEqual(day_2.interval_ids[1].requested_hours, 4.0)

        day_3 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 4)
        )
        day_3.interval_ids[0].requested_hours = 4.0
        day_3.interval_ids[0]._onchange_requested_hours()
        self.assertEqual(day_3.interval_ids[0].requested_hours, 4.0)
        day_3.interval_ids[1].requested_hours = 0.0
        day_3.interval_ids[1]._onchange_requested_hours()
        self.assertEqual(day_3.interval_ids[1].requested_hours, 0.0)

        day_4 = wizard.day_ids.filtered(
            lambda day: day.date == date(2019, 4, 5)
        )
        day_4.interval_ids[0].requested_hours = 4.0
        day_4.interval_ids[0]._onchange_requested_hours()
        self.assertEqual(day_4.interval_ids[0].available_days, 0.5)
        self.assertEqual(day_4.interval_ids[0].requested_hours, 4.0)
        day_4.interval_ids[1].requested_days = 0.5
        day_4.interval_ids[1]._onchange_requested_days()
        self.assertEqual(day_4.interval_ids[1].available_days, 0.5)
        self.assertEqual(day_4.interval_ids[1].requested_hours, 4.0)
        self.assertEqual(day_4.requested_days, 1.0)

        leaves = wizard.generate_leaves()
        self.assertEqual(len(leaves), 3)

        leave_1 = leaves.filtered(
            lambda leave: leave.name == 'test_7 (1/3)'
        )
        self.assertTrue(leave_1)
        self.assertEqual(leave_1.number_of_days, 0.5)

        leave_2 = leaves.filtered(
            lambda leave: leave.name == 'test_7 (2/3)'
        )
        self.assertTrue(leave_2)
        self.assertEqual(leave_2.number_of_days, 1.5)

        leave_3 = leaves.filtered(
            lambda leave: leave.name == 'test_7 (3/3)'
        )
        self.assertTrue(leave_3)
        self.assertEqual(leave_3.number_of_days, 1.0)

    def test_8(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #8',
            'allocation_type': 'fixed',
            'validity_start': False,
            'request_unit': 'hour',
        })
        user = self.SudoUser.create({
            'company_id': self.main_company.id,
            'name': 'User #8',
            'login': 'user_8',
            'email': 'user_8@yourcompany.com',
            'groups_id': [(6, 0, [self.group_user.id])],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #8',
            'user_id': user.id,
        })
        self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 10.0,
        })

        wizard = self.Wizard.sudo(user).create({
            'name': 'test_7',
            'leave_type_id': leave_type.id,
            'date_from': date(2019, 4, 7),
            'date_to': date(2019, 4, 1),
        })
        self.assertEqual(wizard.employee_id, employee)
        wizard._onchange_date_range()
        self.assertEqual(wizard.date_from, wizard.date_to)
        wizard.day_ids._compute_name()
        wizard.interval_ids._compute_name()
