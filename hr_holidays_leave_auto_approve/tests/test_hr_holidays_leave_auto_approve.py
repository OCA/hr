# Copyright 2016-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase


class TestHolidaysAutoValidate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env['res.users']
        self.leave_type_model = self.env['hr.leave.type']
        self.leave_request_model = self.env['hr.leave']
        self.leave_allocation_model = self.env['hr.leave.allocation']

        # Create an employee user to make leave requests
        self.test_user_id = self.user_model.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'mymail@test.com'
        })

        # Create an employee related to the user to make leave requests
        self.test_employee_id = self.employee_model.create(
            {'name': 'Test Employee', 'user_id': self.test_user_id.id})

        # Create 2 leave type
        self.test_leave_type1_id = self.leave_type_model.create(
            {'name': 'Test Leave Type1', 'auto_approve_policy': 'hr'})
        self.test_leave_type2_id = self.leave_type_model.create(
            {'name': 'Test Leave Type2', 'auto_approve_policy': 'no'})

        # Create leave allocation requests for Test Leave Type1 and 2
        self.leave_allocation1 = self.leave_allocation_model.create({
            'name': 'Test Allocation Request 1',
            'holiday_status_id': self.test_leave_type1_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'number_of_days': 10,
        })

        self.leave_allocation2 = self.leave_allocation_model.create({
            'name': 'Test Allocation Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'number_of_days': 10,
        })

    def test_allocation_requests_state(self):
        # Check for leave_allocation1 state
        self.assertEqual(self.leave_allocation1.state, 'confirm')

        # Check for leave_allocation2 state
        self.assertEqual(self.leave_allocation2.state, 'confirm')

    def test_leave_requests_state(self):

        # Validate the leave_allocation2
        self.leave_allocation2.action_approve()

        # Check for leave_allocation2 state
        self.assertEqual(self.leave_allocation2.state, 'validate')

        today = datetime.today()

        # Create leave requests for Leave Type1 and 2
        leave1 = self.leave_request_model.create({
            'name': 'Test Leave Request 1',
            'holiday_status_id': self.test_leave_type1_id.id,
            'date_from': today,
            'date_to': today + timedelta(days=1),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
        })

        leave2 = self.leave_request_model.create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'date_from': today + timedelta(days=5),
            'date_to': today + timedelta(days=8),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
        })

        # Check for leave1 state
        self.assertEqual(leave1.state, 'validate')

        # Check for leave2 state
        self.assertEqual(leave2.state, 'confirm')

    def test_leave_requests_state_employee_user(self):

        today = datetime.today()

        # Create leave requests for Leave Type1 and 2
        leave1 = self.leave_request_model.sudo(self.test_user_id).create({
            'name': 'Test Leave Request 1',
            'holiday_status_id': self.test_leave_type1_id.id,
            'date_from': today + timedelta(days=10),
            'date_to': today + timedelta(days=12),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
        })

        leave2 = self.leave_request_model.sudo(self.test_user_id).create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'holiday_type': 'employee',
            'date_from': today + timedelta(days=13),
            'date_to': today + timedelta(days=14),
            'employee_id': self.test_employee_id.id,
        })

        # Check for leave1 state
        self.assertEqual(leave1.state, 'validate')

        # Check for leave2 state
        self.assertEqual(leave2.state, 'confirm')

    def test_leave_request_employee_validate_all(self):
        self.test_user_id.groups_id = [
            (6, 0, [self.env.ref('base.group_user').id])
        ]

        today = datetime.today()
        self.test_leave_type2_id.write({'auto_approve_policy': 'all'})

        leave1 = self.leave_request_model.sudo(self.test_user_id).create({
            'name': 'Test Leave Request 1',
            'holiday_status_id': self.test_leave_type1_id.id,
            'date_from': today + timedelta(days=10),
            'date_to': today + timedelta(days=12),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
        })

        leave2 = self.leave_request_model.sudo(self.test_user_id).create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'holiday_type': 'employee',
            'date_from': today + timedelta(days=13),
            'date_to': today + timedelta(days=14),
            'employee_id': self.test_employee_id.id,
        })

        # Check for leave1 state
        self.assertEqual(leave1.state, 'confirm')

        # Check for leave2 state
        self.assertEqual(leave2.state, 'validate')
