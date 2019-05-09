# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta, datetime


class TestDutyShift(TransactionCase):
    def setUp(self):
        super(TestDutyShift, self).setUp()
        self.calendar = self.env['resource.calendar'].create({
            'name': 'Calendar',
            'attendance_ids': [(0, 0, {
                'name': 'Monday Morning',
                'dayofweek': '0',
                'hour_from': 8,
                'hour_to': 16
            })]
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'resource_calendar_id': self.calendar.id,
            'address_id': self.env['res.partner'].create(
                {
                    'name': 'Employee 1',
                    'country_id': self.env.ref('base.sl').id
                }
            ).id
        })  # This employee works 8 hours every monday
        today = fields.Date.from_string(fields.Date.today())
        self.date = today + timedelta(days=-today.weekday())
        self.start_date = datetime.combine(self.date, datetime.min.time())
        self.end_date = self.start_date + timedelta(hours=3)

    def create_shift(self):
        return self.env['hr.duty.shift'].create({
            'employee_id': self.employee.id,
            'start_date': fields.Datetime.to_string(self.start_date),
            'end_date': fields.Datetime.to_string(self.end_date),
        })

    def test_duty_shift_name(self):
        shift = self.create_shift()
        self.assertEqual(shift.display_name, '%s - %s' % (
            self.employee.name, self.date.strftime('%Y-%m-%d')
        ))

    def test_resource(self):
        result = self.employee.with_context(
            employee_id=self.employee.id,
            exclude_public_holidays=True,
        ).get_work_days_data(
            self.start_date, self.start_date + timedelta(days=1))
        self.assertEqual(8, result['hours'])
        # Without duties we expect to work 8 hours
        self.create_shift()
        result = self.employee.with_context(
            employee_id=self.employee.id,
            exclude_public_holidays=True,
        ).get_work_days_data(
            self.start_date, self.start_date + timedelta(days=1))
        self.assertEqual(11, result['hours'])
        # With the duty we expect to work 11 hours ( 8 + 3 )

    def test_resource_holiday(self):
        result = self.employee.with_context(
            employee_id=self.employee.id,
            exclude_public_holidays=True,
        ).get_work_days_data(
            self.start_date, self.start_date + timedelta(days=1))
        self.assertEqual(8, result['hours'])
        # Without a holiday we expect to work 8 hours
        self.env['hr.holidays.public'].create({
            'line_ids': [(0, 0, {
                'name': 'holiday',
                'date': fields.Date.to_string(self.date),
            })],
        })
        result = self.employee.with_context(
            employee_id=self.employee.id,
            exclude_public_holidays=True,
        ).get_work_days_data(
            self.start_date, self.start_date + timedelta(days=1))
        self.assertEqual(0, result['hours'])
        # With a holiday we expect to work 0 hours
        self.create_shift()
        result = self.employee.with_context(
            employee_id=self.employee.id,
            exclude_public_holidays=True,
        ).get_work_days_data(
            self.start_date, self.start_date + timedelta(days=1))
        self.assertEqual(3, result['hours'])
        # With the duty we expect to work 3 hours, as it ignores public
        # holidays
