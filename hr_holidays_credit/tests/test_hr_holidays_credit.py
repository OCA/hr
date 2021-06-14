# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class TestHrHolidaysCredit(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.Employee = self.env["hr.employee"]
        self.SudoEmployee = self.Employee.sudo()
        self.Department = self.env["hr.department"]
        self.SudoDepartment = self.Department.sudo()
        self.LeaveType = self.env["hr.leave.type"]
        self.SudoLeaveType = self.LeaveType.sudo()
        self.Leave = self.env["hr.leave"]
        self.SudoLeave = self.Leave.sudo()
        self.LeaveAllocation = self.env["hr.leave.allocation"]

        self.in_hours_w_credit_leave_type = self.SudoLeaveType.create(
            {
                "name": "Recuperation w/ credit",
                "request_unit": "hour",
                "allocation_type": "fixed",
                "allow_credit": True,
            }
        )

        self.in_hours_wo_credit_leave_type = self.SudoLeaveType.create(
            {
                "name": "Recuperation w/o credit",
                "request_unit": "hour",
                "allocation_type": "fixed",
                "allow_credit": False,
            }
        )

        self.in_days_w_credit_leave_type = self.SudoLeaveType.create(
            {
                "name": "Legal w/ credit",
                "request_unit": "day",
                "allocation_type": "fixed",
                "allow_credit": True,
            }
        )

        self.in_days_wo_credit_leave_type = self.SudoLeaveType.create(
            {
                "name": "Legal w/o credit",
                "request_unit": "day",
                "allocation_type": "fixed",
                "allow_credit": False,
            }
        )

    def test_credit_leave_should_not_be_created_if_disabled_on_leave_type(self):
        employee = self.SudoEmployee.create({"name": "Employee #1"})

        with self.assertRaises(ValidationError):
            self.SudoLeave.create(
                {
                    "holiday_status_id": self.in_days_wo_credit_leave_type.id,
                    "holiday_type": "employee",
                    "employee_id": employee.id,
                    "number_of_days": 1,
                }
            )

    def test_credit_leave_should_be_created_if_enable_on_leave_type(self):
        employee = self.SudoEmployee.create({"name": "Employee #2"})

        self.SudoLeave.create(
            {
                "holiday_status_id": self.in_days_w_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )

    def test_leave_credit_conditionned_by_departement(self):
        department = self.SudoDepartment.create({"name": "Department #3"})
        employee_1 = self.SudoEmployee.create(
            {"name": "Employee #3-1", "department_id": department.id}
        )
        employee_2 = self.SudoEmployee.create({"name": "Employee #3-2"})
        leave_type = self.SudoLeaveType.create(
            {
                "name": "Leave Type #3",
                "allocation_type": "fixed",
                "allow_credit": True,
                "creditable_department_ids": [(6, False, [department.id])],
            }
        )

        self.SudoLeave.create(
            {
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee_1.id,
                "number_of_days": 1,
            }
        )

        with self.assertRaises(ValidationError):
            self.SudoLeave.create(
                {
                    "holiday_status_id": leave_type.id,
                    "holiday_type": "employee",
                    "employee_id": employee_2.id,
                    "number_of_days": 1,
                }
            )

    def test_leave_credit_conditionned_by_employee(self):
        employee_1 = self.SudoEmployee.create({"name": "Employee #4-1"})
        employee_2 = self.SudoEmployee.create({"name": "Employee #4-2"})
        leave_type = self.SudoLeaveType.create(
            {
                "name": "Leave Type #4",
                "allocation_type": "fixed",
                "allow_credit": True,
                "creditable_employee_ids": [(6, False, [employee_1.id])],
            }
        )

        self.SudoLeave.create(
            {
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee_1.id,
                "number_of_days": 1,
            }
        )

        with self.assertRaises(ValidationError):
            self.SudoLeave.create(
                {
                    "holiday_status_id": leave_type.id,
                    "holiday_type": "employee",
                    "employee_id": employee_2.id,
                    "number_of_days": 1,
                }
            )

    def test_1_day_available_without_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #5"})
        leave_type = self.in_days_wo_credit_leave_type
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 1",
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )
        alloc.action_approve()

        name = self.in_days_wo_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertEqual("%s (1 day available)" % (leave_type.name), name)

    def test_1_day_available_with_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #5"})
        leave_type = self.in_days_w_credit_leave_type
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 1",
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )
        alloc.action_approve()

        name = self.in_days_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertEqual("%s (1 day available + credit)" %
                         (leave_type.name), name)

    def test_10_days_available_without_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #5"})
        leave_type = self.in_days_wo_credit_leave_type
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 1",
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 10,
            }
        )
        alloc.action_approve()

        name = self.in_days_wo_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertEqual("%s (10 days available)" % (leave_type.name), name)

    def test_11_days_available_with_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #5"})
        leave_type = self.in_days_w_credit_leave_type
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 1",
                "holiday_status_id": leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 11,
            }
        )
        alloc.action_approve()

        name = self.in_days_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertEqual("%s (11 days available + credit)" %
                         (leave_type.name), name)

    def test_0_hour_leave_available_with_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #6"})
        name = self.in_hours_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn("0 hour available", name)
        self.assertIn(" + credit", name)

    def test_2_days_used_in_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #7"})
        self.SudoLeave.create(
            {
                "holiday_status_id": self.in_days_w_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 2,
            }
        )

        name = self.in_days_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn("2 days used in credit", name)

    def test_x_hours_used_in_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #8"})
        leave = self.SudoLeave.create(
            {
                "holiday_status_id": self.in_hours_w_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )

        name = self.in_hours_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn(
            "%g hours used in credit" % abs(
                leave.number_of_hours_display), name
        )
        self.assertNotIn(" + credit", name)

    def test_less_than_1_hour_available_without_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #9"})
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 2",
                "holiday_status_id": self.in_hours_wo_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": round(1 / 9, 1),
            }
        )
        alloc.action_approve()

        name = self.in_hours_wo_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn("%g hour available" %
                      alloc.number_of_hours_display, name)
        self.assertNotIn(" + credit", name)

    def test_x_hours_available_without_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #9"})
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 2",
                "holiday_status_id": self.in_hours_wo_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )
        alloc.action_approve()

        name = self.in_hours_wo_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn("%g hours available" %
                      alloc.number_of_hours_display, name)
        self.assertNotIn(" + credit", name)

    def test_x_hours_available_with_credit_display_name(self):
        employee = self.SudoEmployee.create({"name": "Employee #9"})
        alloc = self.LeaveAllocation.create(
            {
                "name": "Test Allocation 90",
                "holiday_status_id": self.in_hours_w_credit_leave_type.id,
                "holiday_type": "employee",
                "employee_id": employee.id,
                "number_of_days": 1,
            }
        )
        alloc.action_approve()

        name = self.in_hours_w_credit_leave_type.with_context(
            employee_id=employee.id
        ).name_get()[0][1]
        self.assertIn("%g hours available + credit"
                      % alloc.number_of_hours_display, name)
