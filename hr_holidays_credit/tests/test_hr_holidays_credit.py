# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class TestHrHolidaysCredit(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.Department = self.env['hr.department']
        self.SudoDepartment = self.Department.sudo()
        self.LeaveType = self.env['hr.leave.type']
        self.SudoLeaveType = self.LeaveType.sudo()
        self.Leave = self.env['hr.leave']
        self.SudoLeave = self.Leave.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #1',
            'allocation_type': 'fixed',
            'allow_credit': False,
        })

        with self.assertRaises(ValidationError):
            self.SudoLeave.create({
                'holiday_status_id': leave_type.id,
                'holiday_type': 'employee',
                'employee_id': employee.id,
                'number_of_days': 1,
            })

    def test_2(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #2',
            'allocation_type': 'fixed',
            'allow_credit': True,
        })

        self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'number_of_days': 1,
        })

    def test_3(self):
        department = self.SudoDepartment.create({
            'name': 'Department #3',
        })
        employee_1 = self.SudoEmployee.create({
            'name': 'Employee #3-1',
            'department_id': department.id,
        })
        employee_2 = self.SudoEmployee.create({
            'name': 'Employee #3-2',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #3',
            'allocation_type': 'fixed',
            'allow_credit': True,
            'creditable_department_ids': [(6, False, [department.id])],
        })

        self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee_1.id,
            'number_of_days': 1,
        })

        with self.assertRaises(ValidationError):
            self.SudoLeave.create({
                'holiday_status_id': leave_type.id,
                'holiday_type': 'employee',
                'employee_id': employee_2.id,
                'number_of_days': 1,
            })

    def test_4(self):
        employee_1 = self.SudoEmployee.create({
            'name': 'Employee #4-1',
        })
        employee_2 = self.SudoEmployee.create({
            'name': 'Employee #4-2',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #4',
            'allocation_type': 'fixed',
            'allow_credit': True,
            'creditable_employee_ids': [(6, False, [employee_1.id])],
        })

        self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee_1.id,
            'number_of_days': 1,
        })

        with self.assertRaises(ValidationError):
            self.SudoLeave.create({
                'holiday_status_id': leave_type.id,
                'holiday_type': 'employee',
                'employee_id': employee_2.id,
                'number_of_days': 1,
            })

    def test_5(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #5',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #5',
            'allocation_type': 'fixed',
            'allow_credit': False,
        })

        name = leave_type.with_context(
            employee_id=employee.id,
        ).name_get()[0][1]
        self.assertTrue('available' in name)
        self.assertTrue('credit' not in name)

    def test_6(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #6',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #6',
            'allocation_type': 'fixed',
            'allow_credit': True,
        })

        name = leave_type.with_context(
            employee_id=employee.id,
        ).name_get()[0][1]
        self.assertTrue('available + credit' in name)

    def test_7(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #7',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #7',
            'allocation_type': 'fixed',
            'allow_credit': True,
        })
        self.SudoLeave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'number_of_days': 1,
        })

        name = leave_type.with_context(
            employee_id=employee.id,
        ).name_get()[0][1]
        self.assertTrue('used in credit' in name)
