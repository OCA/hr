# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.fields import Date
from datetime import timedelta


class TestResourceCalendar(TransactionCase):
    def setUp(self):
        super().setUp()
        self.calendar = self.env['resource.calendar'].create({
            'name': 'Test calendar 1',
            'attendance_ids': [],
        })
        self.attendance_01 = self.env['resource.calendar.attendance'].create({
            'name': '1',
            'dayofweek': '0',
            'hour_from': 8,
            'hour_to': 12,
            'date_from': False,
            'calendar_id': self.calendar.id,
        })
        self.attendance_02 = self.env['resource.calendar.attendance'].create({
            'name': '2',
            'dayofweek': '0',
            'hour_from': 13,
            'hour_to': 14,
            'date_from': False,
            'calendar_id': self.calendar.id,
        })
        self.attendance_03 = self.env['resource.calendar.attendance'].create({
            'name': '2',
            'dayofweek': '1',
            'hour_from': 13,
            'hour_to': 14,
            'date_from': False,
            'calendar_id': self.calendar.id,
        })

    def test_onchange(self):
        attendance = self.env['resource.calendar.attendance'].new({
            'name': '1',
            'dayofweek': '0',
            'hour_from': 8,
            'hour_to': 12,
            'date_from': False,
            'calendar_id': self.calendar.id,
        })
        attendance.calendar_week_number = 2
        attendance.week_number = 2
        attendance.calendar_week_number = 1
        attendance._onchange_calendar_week_number()
        self.assertEqual(1, attendance.week_number)

    def test_standard_behaviour(self):
        today = Date.from_string(Date.today())
        monday = today + timedelta(days=-today.weekday())
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)

    def test_week_behaviour_01(self):
        today = Date.from_string(Date.today())
        monday = today + timedelta(days=-today.weekday())
        self.attendance_01.calendar_week_number = 2
        self.attendance_02.calendar_week_number = 2
        self.attendance_03.calendar_week_number = 2
        if divmod(monday.isocalendar()[1], 2)[1] == 0:
            monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)

    def test_week_behaviour_02(self):
        today = Date.from_string(Date.today())
        monday = today + timedelta(days=-today.weekday())
        self.attendance_01.calendar_week_number = 2
        self.attendance_02.calendar_week_number = 2
        self.attendance_03.calendar_week_number = 2
        self.attendance_02.week_number = 2
        if divmod(monday.isocalendar()[1], 2)[1] == 0:
            monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)

    def test_week_behaviour_03(self):
        today = Date.from_string(Date.today())
        monday = today + timedelta(days=-today.weekday())
        self.attendance_01.calendar_week_number = 3
        self.attendance_02.calendar_week_number = 3
        self.attendance_03.calendar_week_number = 3
        self.attendance_02.week_number = 2
        self.attendance_03.week_number = 3
        if divmod(monday.isocalendar()[1], 3)[1] == 0:
            monday = monday + timedelta(days=7)
        if divmod(monday.isocalendar()[1], 3)[1] == 2:
            monday = monday + timedelta(days=14)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        attendances = self.calendar._get_day_attendances(
            monday + timedelta(days=1), False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertIn(self.attendance_03, attendances)

    def test_week_behaviour_04(self):
        today = Date.from_string(Date.today())
        monday = today + timedelta(days=-today.weekday())
        self.attendance_01.calendar_week_number = 3
        self.attendance_02.calendar_week_number = 3
        self.attendance_03.calendar_week_number = 3
        self.attendance_01.date_from = monday
        self.attendance_02.date_from = monday
        self.attendance_03.date_from = monday
        self.attendance_01.week_number = 1
        self.attendance_02.week_number = 2
        self.attendance_03.week_number = 3
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        monday = monday + timedelta(days=7)
        attendances = self.calendar._get_day_attendances(monday, False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertNotIn(self.attendance_03, attendances)
        attendances = self.calendar._get_day_attendances(
            monday + timedelta(days=1), False, False)
        self.assertNotIn(self.attendance_01, attendances)
        self.assertNotIn(self.attendance_02, attendances)
        self.assertIn(self.attendance_03, attendances)
