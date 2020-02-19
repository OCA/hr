from odoo import fields, tests

from mock import patch

import pytz


class TestEmployee(tests.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._employee = cls.env.ref('hr.employee_chs')  # David Samson
        cls._empty_schedule = cls.env.ref(
            'hr_attendance_schedule.res_calendar_demo_schedule_empty')
        cls._schedule = cls.env.ref(
            'hr_attendance_schedule.res_calendar_demo_schedule')
        cls._employee.resource_calendar_id = cls._schedule

    def test_check_in_out_real(self):
        self._attendance('2017-01-09 08:01:11')
        self._attendance('2017-01-09 11:57:11')
        attendance = self._employee.attendance_ids[0]
        expected_in = self._user_dt_to_system_dt(
            fields.Datetime.to_datetime('2017-01-09 08:01:11'))
        expected_out = self._user_dt_to_system_dt(
            fields.Datetime.to_datetime('2017-01-09 11:57:11'))
        self.assertEqual(expected_in, attendance.real_check_in)
        self.assertEqual(expected_out, attendance.real_check_out)

    def test_check_in_little_before(self):
        self._attendance('2017-01-16 07:57:00')
        self._assert_attendances('2017-01-16 08:00:00', False,
                                 needs_approval=False)

    def test_check_in_little_after(self):
        self._attendance('2017-01-16 08:03:00')
        self._assert_attendances('2017-01-16 08:00:00', False,
                                 needs_approval=False)

    def test_check_out_little_before(self):
        self._attendance('2017-01-02 08:00:00')
        self._attendance('2017-01-02 11:57:00')
        self._assert_attendances('2017-01-02 08:00:00', '2017-01-02 12:00:00',
                                 needs_approval=False)

    def test_check_out_little_after(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 12:03:00')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 12:00:00',
                                 needs_approval=False)

    def test_check_in_too_soon(self):
        self._attendance('2017-01-16 07:22:22')
        self._assert_attendances('2017-01-16 07:22:22', False,
                                 needs_approval=True)

    def test_check_in_too_late(self):
        self._attendance('2017-01-16 08:22:22')
        self._assert_attendances('2017-01-16 08:22:22', False,
                                 needs_approval=True)

    def test_check_out_too_soon(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 11:22:22')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 11:22:22',
                                 needs_approval=True)

    def test_check_out_too_late(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 12:22:22')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 12:22:22',
                                 needs_approval=True)

    def test_check_in_wrong_day(self):
        self._attendance('2017-01-18 07:57:00')
        self._assert_attendances('2017-01-18 07:57:00', False,
                                 needs_approval=True)

    def test_check_in_no_schedule(self):
        self._employee.resource_calendar_id = self._empty_schedule
        self._attendance('2017-01-16 08:01:11')
        self._attendance('2017-01-16 12:02:22')
        self._assert_attendances('2017-01-16 08:01:11', '2017-01-16 12:02:22',
                                 needs_approval=True)

    def test_check_in_before_midnight(self):
        self._attendance('2017-01-19 23:57:11')
        self._attendance('2017-01-20 04:01:11')
        self._assert_attendances('2017-01-20 00:00:00', '2017-01-20 04:00:00',
                                 needs_approval=False)

    def test_check_in_after_midnight(self):
        self._attendance('2017-01-21 00:01:11')
        self._assert_attendances('2017-01-20 23:58:00', False,
                                 needs_approval=False)

    def test_check_out_before_midnight(self):
        self._attendance('2017-01-22 19:57:11')
        self._attendance('2017-01-22 23:58:11')
        self._assert_attendances('2017-01-22 20:00:00', '2017-01-23 00:00:00',
                                 needs_approval=False)

    def test_check_out_after_midnight(self):
        self._attendance('2017-01-22 19:57:11')
        self._attendance('2017-01-23 00:01:11')
        self._assert_attendances('2017-01-22 20:00:00', '2017-01-23 00:00:00',
                                 needs_approval=False)

    def test_check_in_sunday_checkout_monday(self):
        self._attendance('2017-01-22 21:58:00')
        self._attendance('2017-01-23 02:02:00')
        self._assert_attendances('2017-01-22 22:00:00', '2017-01-23 02:00:00',
                                 needs_approval=False)

    def test_check_in_before_date_from(self):
        self._attendance('2016-01-04 07:57:00')
        self._assert_attendances('2016-01-04 07:57:00', False,
                                 needs_approval=True)

    def test_check_in_after_date_to(self):
        self._attendance('2018-01-08 07:57:00')
        self._assert_attendances('2018-01-08 07:57:00', False,
                                 needs_approval=True)

    def test_check_out_before_date_from(self):
        self._attendance('2016-01-04 08:00:00')
        self._attendance('2016-01-04 11:57:00')
        self._assert_attendances('2016-01-04 08:00:00', '2016-01-04 11:57:00',
                                 needs_approval=True)

    def test_check_out_after_date_to(self):
        self._attendance('2018-01-08 08:00:00')
        self._attendance('2018-01-08 11:57:00')
        self._assert_attendances('2018-01-08 08:00:00', '2018-01-08 11:57:00',
                                 needs_approval=True)

    def test_check_in_out_at_date_from(self):
        self._attendance('2017-01-02 07:57:00')
        self._attendance('2017-01-02 11:57:00')
        self._assert_attendances('2017-01-02 08:00:00', '2017-01-02 12:00:00',
                                 needs_approval=False)

    def test_check_in_out_at_date_to(self):
        self._attendance('2017-02-06 07:57:00')
        self._attendance('2017-02-06 11:57:00')
        self._assert_attendances('2017-02-06 08:00:00', '2017-02-06 12:00:00',
                                 needs_approval=False)

    def test_attendance_on_leaf(self):
        self._attendance('2017-03-07 07:57:00')
        self._attendance('2017-03-07 11:57:00')
        self._assert_attendances('2017-03-07 07:57:00', '2017-03-07 11:57:00',
                                 needs_approval=True)

    def _assert_attendances(self, check_in, check_out, needs_approval):
        self.assertEqual(1, len(self._employee.attendance_ids))
        attendance = self._employee.attendance_ids[0]
        check_in = check_in and fields.Datetime.to_datetime(check_in)
        check_out = check_out and fields.Datetime.to_datetime(check_out)
        check_in = self._user_dt_to_system_dt(check_in)
        self.assertEqual(check_in, attendance.check_in)
        if check_out:
            check_out = self._user_dt_to_system_dt(check_out)
            self.assertEqual(check_out, attendance.check_out)
        else:
            self.assertFalse(attendance.check_out)
        self.assertEqual(needs_approval, attendance.needs_approval)

    def _user_dt_to_system_dt(self, user_time):
        user_time = fields.Datetime.to_datetime(user_time)
        user_time = pytz.timezone(self.env.user.tz).localize(user_time)
        return user_time.astimezone(pytz.utc).replace(tzinfo=None)

    def _attendance(self, user_time):
        system_time = self._user_dt_to_system_dt(user_time)
        with patch.object(fields.Datetime, 'now', return_value=system_time):
            self._employee.attendance_manual(
                'hr_attendance.hr_attendance_action_my_attendances')
