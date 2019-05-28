# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import ValidationError
from datetime import datetime, time


class HRCalendarRestTime(TransactionCase):

    def setUp(self):
        super(HRCalendarRestTime, self).setUp()
        self.calendar = self.env['resource.calendar'].create({
            'name': 'Calendar 1',
            'attendance_ids': []
        })
        # We define a 7 days per week working calendar, 8 to 17h (
        # 9 hours in duration) with 1h of rest time.
        for i in range(0, 7):
            self.env['resource.calendar.attendance'].create({
                'name': 'Day ' + str(i),
                'dayofweek': str(i),
                'hour_from': 8.0,
                'hour_to': 17.0,
                'rest_time': 1.0,
                'calendar_id': self.calendar.id,
            })

        self.employee = self.env['hr.employee'].create({
            'name': 'Employee',
            'resource_calendar_id': self.calendar.id
        })

    def test_rest_time(self):
        """We expect that the number of effective working hours
        should be 8 hours"""
        today = fields.Date.from_string(fields.Date.today())
        hours = self.employee.get_work_days_data(
            datetime.combine(today, time(
                0, 0, 0, 0)),
            datetime.combine(
                today, time(23, 59, 59, 99999)),
        )['hours']
        self.assertEqual(hours, 8.0)

        with self.assertRaises(ValidationError):
            self.calendar.attendance_ids[0].write({'rest_time': 10})

        self.calendar.attendance_ids[0].write({'rest_time': -1})
        self.calendar.attendance_ids[0]._onchange_rest_time()
        self.assertEqual(self.calendar.attendance_ids[0].rest_time, 0.0)
