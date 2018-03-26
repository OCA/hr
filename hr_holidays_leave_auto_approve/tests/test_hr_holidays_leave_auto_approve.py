# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class TestHolidaysAutoApprove(TransactionCase):
    def setUp(self):
        super(TestHolidaysAutoApprove, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env['res.users']
        self.leave_type_model = self.env['hr.holidays.status']
        self.leave_request_model = self.env['hr.holidays']

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
            {'name': 'Test Leave Type1', 'auto_approve': True})
        self.test_leave_type2_id = self.leave_type_model.create(
            {'name': 'Test Leave Type2', 'auto_approve': False})

        # Create leave allocation requests for Test Leave Type1 and 2
        self.leave_allocation1 = self.leave_request_model.create({
            'name': 'Test Allocation Request 1',
            'holiday_status_id': self.test_leave_type1_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'number_of_days_temp': 10,
            'type': 'add',
        })

        self.leave_allocation2 = self.leave_request_model.create({
            'name': 'Test Allocation Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'number_of_days_temp': 10,
            'type': 'add',
        })

    def test_allocation_requests_state(self):
        # Check for leave_allocation1 state
        self.assertEqual(self.leave_allocation1.state, 'validate')

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
            'date_from': today.strftime(DF),
            'date_to': (today + timedelta(days=1)).strftime(DF),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
        })

        leave2 = self.leave_request_model.create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'date_from': (today + timedelta(days=5)).strftime(DF),
            'date_to': (today + timedelta(days=8)).strftime(DF),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
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
            'date_from': (today + timedelta(days=10)).strftime(DF),
            'date_to': (today + timedelta(days=12)).strftime(DF),
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
        })

        leave2 = self.leave_request_model.sudo(self.test_user_id).create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type2_id.id,
            'holiday_type': 'employee',
            'date_from': (today + timedelta(days=13)).strftime(DF),
            'date_to': (today + timedelta(days=14)).strftime(DF),
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
        })

        # Check for leave1 state
        self.assertEqual(leave1.state, 'validate')

        # Check for leave2 state
        self.assertEqual(leave2.state, 'confirm')
