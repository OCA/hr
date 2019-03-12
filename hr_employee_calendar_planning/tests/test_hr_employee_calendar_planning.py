# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from ..hooks import post_init_hook


class TestHrEmployeeCalendarPlanning(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrEmployeeCalendarPlanning, cls).setUpClass()
        cls.calendar1 = cls.env['resource.calendar'].create({
            'name': 'Test calendar 1',
        })
        cls.calendar2 = cls.env['resource.calendar'].create({
            'name': 'Test calendar 2',
        })
        for day in range(5):  # From monday to friday
            cls.calendar1.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '12',
                }),
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '14',
                    'hour_to': '18',
                }),
            ]
            cls.calendar2.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '07',
                    'hour_to': '14',
                }),
            ]
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test employee',
        })

    def test_calendar_planning(self):
        self.employee.calendar_ids = [
            (0, 0, {
                'date_end': '2019-12-31',
                'calendar_id': self.calendar1.id,
            }),
            (0, 0, {
                'date_start': '2020-01-01',
                'calendar_id': self.calendar2.id,
            }),
        ]
        self.assertTrue(self.employee.calendar_id)
        calendar = self.employee.calendar_id
        self.assertEqual(len(calendar.attendance_ids), 15)
        self.assertEqual(len(calendar.attendance_ids.filtered(
            lambda x: x.date_from == '2020-01-01'
        )), 5)
        self.assertEqual(len(calendar.attendance_ids.filtered(
            lambda x: x.date_to == '2019-12-31'
        )), 10)
        # Change one line
        calendar_line = self.employee.calendar_ids[0]
        calendar_line.date_end = '2019-12-30'
        calendar = self.employee.calendar_id
        self.assertEqual(len(calendar.attendance_ids.filtered(
            lambda x: x.date_to == '2019-12-30'
        )), 10)

    def test_post_install_hook(self):
        self.employee.calendar_id = self.calendar1.id
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertNotEqual(self.employee.calendar_id, self.calendar1)
        # Check that no change is done on original calendar
        self.assertEqual(len(self.calendar1.attendance_ids), 10)
        self.assertEqual(len(self.employee.calendar_ids), 1)
        self.assertFalse(self.employee.calendar_ids.date_start)
        self.assertFalse(self.employee.calendar_ids.date_end)

    def test_post_install_hook_several_calendaries(self):
        self.calendar1.attendance_ids[0].date_from = '2019-01-01'
        self.calendar1.attendance_ids[1].date_from = '2019-01-01'
        self.employee.calendar_id = self.calendar1.id
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertNotEqual(self.employee.calendar_id, self.calendar1)
        # Check that no change is done on original calendar
        self.assertEqual(len(self.calendar1.attendance_ids), 10)
        self.assertEqual(len(self.employee.calendar_ids), 2)
        self.assertEqual(
            len(self.employee.calendar_ids[0].calendar_id.attendance_ids), 2,
        )
        self.assertEqual(
            len(self.employee.calendar_ids[1].calendar_id.attendance_ids), 8,
        )
