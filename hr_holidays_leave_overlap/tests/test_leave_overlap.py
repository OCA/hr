# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from odoo.tests import common


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
        """When a leave request is created on a period which starts without
        overlapping and ends within another leave request period, the new
        leave request should be adapted to end exactly before the overlapping
        period starts"""
        self.leave_request_model.create({
            'name': 'Test Leave Request A',
            'holiday_status_id': self.test_leave_type_id.id,
            'holiday_type': 'employee',
            'employee_id': self.test_employee_id.id,
            'type': 'remove',
            'date_from': Datetime.to_string(self.today - timedelta(days=2)),
            'date_to': Datetime.to_string(self.today + timedelta(days=1))
        })

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today - timedelta(days=2))),
            ('date_to', '=', Datetime.to_string(
                self.today - timedelta(seconds=1)))
        ])
        self.assertNotEquals(res, False)

    def test_02_right(self):
        """When a leave request is created on a period which starts within
        another leave request period and ends without overlapping, the new
        leave request should be adapted to start exactly after the overlapping
        period ends"""
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

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=11, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=12)))
        ])
        self.assertNotEquals(res, False)

    def test_03_including(self):
        """When a leave request is created on a period which starts and ends
        without overlapping but including a period already covered by another,
        leave request, the new leave request should be splitted in order to
        create two leave requests, one covering the period right before the
        overlapping period and the other covering the period right after the
        overlapping period."""
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

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=3))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=4) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(res, False)

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=7, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=8)))
        ])
        self.assertNotEquals(res, False)

    def test_04_included(self):
        """When a leave request is created on a period completely included in
        the period of an already existing leave request, the system shouldn't
        allow it and raise a ValidationError"""
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
        """This test will check the more complex case in which a new leave
        request's period includes multiple distinct periods covered by already
         existing leave requests. In this case, the system is expected to
         create multiple non-overlapping leave requests filling the gaps"""
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

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today - timedelta(days=1))),
            ('date_to', '=', Datetime.to_string(
                self.today - timedelta(seconds=1)))
        ])
        self.assertNotEquals(res, False)

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=2, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=4) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(res, False)

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=7, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=9) - timedelta(seconds=1)))
        ])
        self.assertNotEquals(res, False)

        res = self.leave_request_model.search([
            ('employee_id', '=', self.test_employee_id.id),
            ('date_from', '=', Datetime.to_string(
                self.today + timedelta(days=11, seconds=1))),
            ('date_to', '=', Datetime.to_string(
                self.today + timedelta(days=13)))
        ])
        self.assertNotEquals(res, False)
