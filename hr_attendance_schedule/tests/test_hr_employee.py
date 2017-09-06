# -*- coding: utf-8 -*-
from mock import patch

from odoo import fields, tests


class TestEmployee(tests.SingleTransactionCase):
    _employee = None
    _schedule = None
    
    def setUp(self):
        super(TestEmployee, self).setUp()
        self._init_employee()
        self._init_schedule()

    def tearDown(self):
        self._employee.attendance_ids.unlink()
        self._employee.schedule_id = self._schedule
        super(TestEmployee, self).tearDown()

    def _init_employee(self):
        if not self._employee:
            self._employee = self.env.ref('hr.employee_chs') #David Samson

    def _init_schedule(self):
        if not self._schedule:
            self._schedule = self.env.ref('hr_attendance_schedule.hr_attendance_schedule_demo_schedule')
            self._schedule.write({ 'employee_ids': [ (4, self._employee.id) ] })

    def test_check_in_out_real(self):
        self._attendance('2017-01-09 08:01:11')
        self._attendance('2017-01-09 11:57:11')
        attendance = self._employee.attendance_ids[0]
        self.assertEqual('2017-01-09 08:01:11', attendance.real_check_in)
        self.assertEqual('2017-01-09 11:57:11', attendance.real_check_out)

    def test_check_in_little_before(self):
        self._attendance('2017-01-16 07:57:00')
        self._assert_attendances('2017-01-16 08:00:00', False, needs_approval=False)

    def test_check_in_little_after(self):
        self._attendance('2017-01-16 08:03:00')
        self._assert_attendances('2017-01-16 08:00:00', False, needs_approval=False)

    def test_check_out_little_before(self):
        self._attendance('2017-01-02 08:00:00')
        self._attendance('2017-01-02 11:57:00')
        self._assert_attendances('2017-01-02 08:00:00', '2017-01-02 12:00:00', needs_approval=False)

    def test_check_out_little_after(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 12:03:00')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 12:00:00', needs_approval=False)

    def test_check_in_too_soon(self):
        self._attendance('2017-01-16 07:22:22')
        self._assert_attendances('2017-01-16 07:22:22', False, needs_approval=True)

    def test_check_in_too_late(self):
        self._attendance('2017-01-16 08:22:22')
        self._assert_attendances('2017-01-16 08:22:22', False, needs_approval=True)

    def test_check_out_too_soon(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 11:22:22')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 11:22:22', needs_approval=True)

    def test_check_out_too_late(self):
        self._attendance('2017-01-16 08:00:00')
        self._attendance('2017-01-16 12:22:22')
        self._assert_attendances('2017-01-16 08:00:00', '2017-01-16 12:22:22', needs_approval=True)

    def test_check_in_wrong_day(self):
        self._attendance('2017-01-18 07:57:00')
        self._assert_attendances('2017-01-18 07:57:00', False, needs_approval=True)

    def test_check_in_no_schedule(self):
        self._employee.schedule_id = None
        self._attendance('2017-01-16 08:01:11')
        self._attendance('2017-01-16 12:02:22')
        self._assert_attendances('2017-01-16 08:01:11', '2017-01-16 12:02:22', needs_approval=True)

    def test_check_in_before_midnight(self):
        self._attendance('2017-01-19 23:57:11')
        self._attendance('2017-01-20 04:01:11')
        self._assert_attendances('2017-01-20 00:00:00', '2017-01-20 04:00:00', needs_approval=False)

    def test_check_in_after_midnight(self):
        self._attendance('2017-01-21 00:01:11')
        self._assert_attendances('2017-01-20 23:58:00', False, needs_approval=False)

    def test_check_out_before_midnight(self):
        self._attendance('2017-01-22 19:57:11')
        self._attendance('2017-01-22 23:58:11')
        self._assert_attendances('2017-01-22 20:00:00', '2017-01-23 00:00:00', needs_approval=False)

    def test_check_out_after_midnight(self):
        self._attendance('2017-01-22 19:57:11')
        self._attendance('2017-01-23 00:01:11')
        self._assert_attendances('2017-01-22 20:00:00', '2017-01-23 00:00:00', needs_approval=False)

    def _assert_attendances(self, check_in, check_out, needs_approval):
        self.assertEqual(1, len(self._employee.attendance_ids))
        attendance = self._employee.attendance_ids[0]
        self.assertEqual(needs_approval, attendance.needs_approval)
        self.assertEqual(check_in, attendance.check_in)
        if check_out:
            self.assertEqual(check_out, attendance.check_out)
        else:
            self.assertFalse(attendance.check_out)

    def _attendance(self, time):
        with patch.object(fields.Datetime, 'now', return_value=time):
            self._employee.attendance_manual('hr_attendance.hr_attendance_action_my_attendances')
