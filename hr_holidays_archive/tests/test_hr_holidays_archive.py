# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrHolidaysArchive(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrEmployee = self.env['hr.employee']
        self.HrLeaveType = self.env['hr.leave.type']
        self.HrLeave = self.env['hr.leave']
        self.HrLeaveAllocation = self.env['hr.leave.allocation']
        self.now = fields.Datetime.now()

    def test_archived_allocation(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        leave_type = self.HrLeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
        })
        self.HrLeaveAllocation.create({
            'name': 'Allocation',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 5,
        })
        allocation_2 = self.HrLeaveAllocation.create({
            'name': 'Allocation 2',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 5,
        })

        leave_type = leave_type.with_context(
            employee_id=employee.id,
        )

        leave_type._compute_leaves()
        self.assertEqual(len(self.HrLeaveAllocation.search([
            ('holiday_status_id', '=', leave_type.id),
        ])), 2)
        self.assertEqual(leave_type.remaining_leaves, 10)
        self.assertEqual(leave_type.virtual_remaining_leaves, 10)

        allocation_2.active = False
        leave_type._compute_leaves()
        self.assertEqual(len(self.HrLeaveAllocation.search([
            ('holiday_status_id', '=', leave_type.id),
        ])), 1)
        self.assertEqual(leave_type.remaining_leaves, 5)
        self.assertEqual(leave_type.virtual_remaining_leaves, 5)

    def test_archive_validated_request(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        leave_type = self.HrLeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
        })
        self.HrLeaveAllocation.create({
            'name': 'Allocation',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 5,
        })

        leave = self.HrLeave.create({
            'name': 'Leave',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'date_from': self.now,
            'date_to': self.now + relativedelta(weeks=1),
            'number_of_days': 1.0,
            'state': 'validate',
        })

        with self.assertRaises(ValidationError):
            leave.active = False

    def test_archive_refused_request(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        leave_type = self.HrLeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
        })
        self.HrLeaveAllocation.create({
            'name': 'Allocation',
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'number_of_days': 5,
        })

        leave = self.HrLeave.create({
            'name': 'Leave',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'date_from': self.now,
            'date_to': self.now + relativedelta(weeks=1),
            'number_of_days': 1.0,
            'state': 'refuse',
        })

        leave.active = False
