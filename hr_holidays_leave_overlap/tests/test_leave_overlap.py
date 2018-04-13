# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.fields import Datetime
from datetime import timedelta


class TestLeaveOverlap(common.TransactionCase):

    def setUp(self):
        super(TestLeaveOverlap, self).setUp()

        self.employee_model = self.env['hr.employee']
        self.user_model = self.env['res.users']
        self.leave_type_model = self.env['hr.holidays.status']
        self.leave_request_model = self.env['hr.holidays']
        self.today = Datetime.from_string(Datetime.now()).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Create an employee user to make leave requests
        self.test_user_id = self.user_model.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'mymail@test.com'
        })

        # Create an employee related to the user to make leave requests
        self.test_employee_id = self.employee_model.create(
            {'name': 'Test Employee', 'user_id': self.test_user_id.id})

        # Create 1 leave type
        self.test_leave_type_id = self.leave_type_model.create(
            {'name': 'Test Leave Type1'})

        # Create some leave request
        self.leave_request1 = self.leave_request_model.create({
            'name': 'Test Leave Request 1',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(self.today),
            'date_to': Datetime.to_string(self.today + timedelta(days=2))
        })

        self.leave_request2 = self.leave_request_model.create({
            'name': 'Test Leave Request 2',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(self.today + timedelta(days=4)),
            'date_to': Datetime.to_string(self.today + timedelta(days=7))
        })

        self.leave_request3 = self.leave_request_model.create({
            'name': 'Test Leave Request 3',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(self.today + timedelta(days=9)),
            'date_to': Datetime.to_string(self.today + timedelta(days=11))
        })

    def test_01_left(self):
        self.leave_request_model.create({
            'name': 'Test Leave Request A',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(self.today - timedelta(days=2)),
            'date_to': Datetime.to_string(self.today + timedelta(days=1))
        })

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today - timedelta(days=2))),
            ('date_to', '=', Datetime.to_string(
                self.today - timedelta(seconds=1)))
        ])
        self.assertNotEquals(r, False)

    def test_02_right(self):
        self.leave_request_model.create({
            'name': 'Test Leave Request B',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(
                self.today + timedelta(days=9)),
            'date_to': Datetime.to_string(
                self.today + timedelta(days=12))
        })

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=11, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=12)))
        ])
        self.assertNotEquals(r, False)

    def test_03_including(self):
        self.leave_request_model.create({
            'name': 'Test Leave Request C',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(
                self.today + timedelta(days=3)),
            'date_to': Datetime.to_string(
                self.today + timedelta(days=8))
        })

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=3))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=4) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(r, False)

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=7, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=8)))
        ])
        self.assertNotEquals(r, False)

    def test_04_included(self):
        with self.assertRaises(ValidationError):
            self.leave_request_model.create({
                'name': 'Test Leave Request D',
                'holiday_status_id': self.test_leave_type_id.id,
                'holiday_type': 'employee',
                'employee_id': self.test_employee_id.id,
                'type': 'remove',
                'date_from': Datetime.to_string(
                    self.today + timedelta(days=5)),
                'date_to': Datetime.to_string(
                    self.today + timedelta(days=6))
            })

    def test_05_all(self):
        self.leave_request_model.create({
            'name': 'Test Leave Request E',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(
                self.today - timedelta(days=1)),
            'date_to': Datetime.to_string(
                self.today + timedelta(days=13))
        })

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today - timedelta(days=1))),
            ('date_to', '=', Datetime.to_string(
                self.today - timedelta(seconds=1)))
        ])
        self.assertNotEquals(r, False)

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=2, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=4) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(r, False)

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=7, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=9) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(r, False)

        r = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=11, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=13)))
        ])
        self.assertNotEquals(r, False)
