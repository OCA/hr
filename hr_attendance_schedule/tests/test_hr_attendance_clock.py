from mock import patch

from odoo import fields, tests


class TestSyncClock(tests.TransactionCase):
    def test_get_time(self):
        now = '2017-01-01 12:12:12'
        with patch.object(fields.Datetime, 'now', return_value=now):
            system_now = self.env['hr_attendance_schedule.clock'].get_system_clock()
            self.assertEqual('2017-01-01T12:12:12+00:00', system_now)
