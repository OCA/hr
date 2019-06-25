# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import UserError

from datetime import datetime, date, time


class TestHrHolidaysLengthValidation(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.tuesday = date(2018, 2, 5)
        self.wednesday = date(2018, 2, 6)
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.LeaveType = self.env['hr.leave.type']
        self.SudoLeaveType = self.LeaveType.sudo()
        self.LeaveAllocation = self.env['hr.leave.allocation']
        self.SudoLeaveAllocation = self.LeaveAllocation.sudo()
        self.Leave = self.env['hr.leave']
        self.SudoLeave = self.Leave.sudo()
        self.ResourceCalendar = self.env['resource.calendar']
        self.SudoResourceCalendar = self.ResourceCalendar.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #1',
            'allocation_type': 'fixed',
            'validity_start': False,
        })

        allocation = self.SudoLeaveAllocation.create({
            'name': 'Allocation #1',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        allocation.action_approve()

        leave = self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.wednesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
            'number_of_days': 0.5,
        })

        with self.assertRaises(UserError):
            leave.action_validate_length()

        leave.action_validate()
        with self.assertRaises(UserError):
            leave.action_validate_length()

    def test_2(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #2',
            'allocation_type': 'fixed',
            'validity_start': False,
        })

        allocation = self.SudoLeaveAllocation.create({
            'name': 'Allocation #2',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        allocation.action_approve()

        leave = self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.wednesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
        })
        leave._onchange_leave_dates()

        leave.action_validate_length()

        leave.action_validate()
        leave.action_validate_length()

    def test_3(self):
        calendar = self.SudoResourceCalendar.create({
            'name': 'Calendar #3',
        })
        calendar.write({
            'global_leave_ids': [
                (0, False, {
                    'name': 'Global Leave #3',
                    'date_from': datetime.combine(self.wednesday, time.min),
                    'date_to': datetime.combine(self.wednesday, time.max),
                }),
            ],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #3',
            'resource_calendar_id': calendar.id,
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #3',
            'allocation_type': 'fixed',
            'validity_start': False,
        })

        allocation = self.SudoLeaveAllocation.create({
            'name': 'Allocation #3',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 2,
        })
        allocation.action_approve()

        leave = self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.tuesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
        })
        leave._onchange_leave_dates()

        leave.action_validate_length()

        leave.action_validate()
        leave.action_validate_length()

    def test_4(self):
        calendar = self.SudoResourceCalendar.create({
            'name': 'Calendar #4',
        })
        calendar.write({
            'global_leave_ids': [
                (0, False, {
                    'name': 'Global Leave #4',
                    'date_from': datetime.combine(self.wednesday, time.min),
                    'date_to': datetime.combine(self.wednesday, time.max),
                }),
            ],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #4',
            'resource_calendar_id': calendar.id,
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #4',
            'allocation_type': 'fixed',
            'validity_start': False,
        })

        allocation = self.SudoLeaveAllocation.create({
            'name': 'Allocation #4',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 2,
        })
        allocation.action_approve()

        leave = self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.tuesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
            'number_of_days': 2,
        })

        with self.assertRaises(UserError):
            leave.action_validate_length()

        leave.action_validate()
        with self.assertRaises(UserError):
            leave.action_validate_length()
