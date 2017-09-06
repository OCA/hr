# -*- coding: utf-8 -*-
from odoo import tests


class TestPeriod(tests.TransactionCase):
    def test_week_day(self):
        period = self.env.ref('hr_attendance_schedule.hr_attendance_schedule_period_5')
        self.assertEqual("Thursday", period.week_day)
