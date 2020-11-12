# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common

from ..hooks import post_init_hook


class TestHrEmployeeCalendarPlanning(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrEmployeeCalendarPlanning, cls).setUpClass()
        resource_calendar = cls.env["resource.calendar"]
        cls.calendar1 = resource_calendar.create(
            {"name": "Test calendar 1", "attendance_ids": []}
        )
        cls.calendar2 = resource_calendar.create(
            {"name": "Test calendar 2", "attendance_ids": []}
        )
        for day in range(5):  # From monday to friday
            cls.calendar1.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "13",
                        "hour_to": "17",
                    },
                ),
            ]
            cls.calendar2.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "07",
                        "hour_to": "14",
                    },
                ),
            ]
        cls.employee = cls.env["hr.employee"].create({"name": "Test employee"})
        cls.leave1 = cls.env["resource.calendar.leaves"].create(
            {
                "name": "Test leave",
                "calendar_id": cls.calendar1.id,
                "resource_id": cls.employee.resource_id.id,
                "date_from": "2019-06-01",
                "date_to": "2019-06-10",
            }
        )

    def test_calendar_planning(self):
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id}),
            (0, 0, {"date_start": "2020-01-01", "calendar_id": self.calendar2.id}),
        ]
        self.assertTrue(self.employee.resource_calendar_id)
        calendar = self.employee.resource_calendar_id
        self.assertEqual(len(calendar.attendance_ids), 15)
        self.assertEqual(
            len(
                calendar.attendance_ids.filtered(
                    lambda x: x.date_from == fields.Date.to_date("2020-01-01")
                )
            ),
            5,
        )
        self.assertEqual(
            len(
                calendar.attendance_ids.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-31")
                )
            ),
            10,
        )

        # Change one line
        calendar_line = self.employee.calendar_ids[0]
        calendar_line.date_end = "2019-12-30"
        calendar = self.employee.resource_calendar_id
        self.assertEqual(
            len(
                calendar.attendance_ids.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-30")
                )
            ),
            10,
        )
        calendar_line.unlink()
        self.assertEqual(
            len(
                calendar.attendance_ids.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-30")
                )
            ),
            0,
        )
        self.assertEqual(len(calendar.attendance_ids), 5)
        self.calendar2.write(
            {
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Attendance",
                            "dayofweek": "6",
                            "hour_from": "08",
                            "hour_to": "12",
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(calendar.attendance_ids), 6)

        # 2 week calendars
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id})
        ]
        self.calendar1.switch_calendar_type()

        self.assertTrue(self.employee.resource_calendar_id.two_weeks_calendar)

        # Calendar 1 has 20 lines + Calendar 2 has 6 lines that are duplicated
        # in the odd and even week + even week label + odd week label
        self.assertEqual(
            len(self.employee.resource_calendar_id.attendance_ids), 20 + 6 * 2 + 2
        )

    def test_post_install_hook(self):
        self.employee.resource_calendar_id = self.calendar1.id
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertNotEqual(self.employee.resource_calendar_id, self.calendar1)
        # Check that no change is done on original calendar
        self.assertEqual(len(self.calendar1.attendance_ids), 10)
        self.assertEqual(len(self.employee.calendar_ids), 1)
        self.assertFalse(self.employee.calendar_ids.date_start)
        self.assertFalse(self.employee.calendar_ids.date_end)
        # Check that the employee leaves are transferred to the new calendar
        self.assertFalse(self.calendar1.leave_ids)
        self.assertEqual(self.employee.resource_calendar_id.leave_ids, self.leave1)

    def test_post_install_hook_several_calendaries(self):
        self.calendar1.attendance_ids[0].date_from = "2019-01-01"
        self.calendar1.attendance_ids[1].date_from = "2019-01-01"
        self.employee.resource_calendar_id = self.calendar1.id
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertNotEqual(self.employee.resource_calendar_id, self.calendar1)
        # Check that no change is done on original calendar
        self.assertEqual(len(self.calendar1.attendance_ids), 10)
        self.assertEqual(len(self.employee.calendar_ids), 2)
        self.assertEqual(
            len(self.employee.calendar_ids[0].calendar_id.attendance_ids), 2,
        )
        self.assertEqual(
            len(self.employee.calendar_ids[1].calendar_id.attendance_ids), 8,
        )
