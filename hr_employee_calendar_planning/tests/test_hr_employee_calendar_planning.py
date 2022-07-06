# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, fields
from odoo.tests import common

from ..hooks import post_init_hook


class TestHrEmployeeCalendarPlanning(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.global_leave1 = cls.env["resource.calendar.leaves"].create(
            {
                "name": "Global Leave 1",
                "date_from": "2019-03-01",
                "date_to": "2019-03-02",
            }
        )
        cls.global_leave2 = cls.env["resource.calendar.leaves"].create(
            {
                "name": "Global Leave 2",
                "date_from": "2020-03-12",
                "date_to": "2020-03-13",
            }
        )
        cls.global_leave3 = cls.env["resource.calendar.leaves"].create(
            {
                "name": "Global Leave 3",
                "date_from": "2020-03-09",
                "date_to": "2020-03-10",
            }
        )
        cls.calendar1.global_leave_ids = [
            (6, 0, [cls.global_leave1.id, cls.global_leave2.id])
        ]
        cls.calendar2.global_leave_ids = [(6, 0, [cls.global_leave3.id])]

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

    def test_calendar_planning_two_weeks(self):
        self.calendar1.switch_calendar_type()
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id}),
            (0, 0, {"date_start": "2020-01-01", "calendar_id": self.calendar2.id}),
        ]
        self.assertEqual(
            len(self.employee.resource_calendar_id.attendance_ids), 20 + 5 * 2 + 2
        )
        items = self.employee.resource_calendar_id.attendance_ids
        items_with_sections = items.filtered(lambda x: x.display_type)
        self.assertEqual(len(items_with_sections), 2)
        items_date_to = items.filtered(
            lambda x: x.date_to == fields.Date.to_date("2019-12-31")
        )
        self.assertEqual(len(items_date_to), 20)
        self.assertEqual(len(items_date_to.filtered(lambda x: x.week_type == "0")), 10)
        self.assertEqual(len(items_date_to.filtered(lambda x: x.week_type == "1")), 10)
        items_date_from = items.filtered(
            lambda x: x.date_from == fields.Date.to_date("2020-01-01")
        )
        self.assertEqual(len(items_date_from), 10)
        self.assertEqual(len(items_date_from.filtered(lambda x: x.week_type == "0")), 5)
        self.assertEqual(len(items_date_from.filtered(lambda x: x.week_type == "1")), 5)
        items_without_sections = items - items_with_sections
        self.assertEqual(
            len(items_without_sections.filtered(lambda x: x.week_type == "0")), 10 + 5
        )
        self.assertEqual(
            len(items_without_sections.filtered(lambda x: x.week_type == "1")), 10 + 5
        )
        self.calendar2.switch_calendar_type()
        items = self.employee.resource_calendar_id.attendance_ids
        items_with_sections = items.filtered(lambda x: x.display_type)
        items_without_sections = items - items_with_sections
        self.assertEqual(len(items), 20 + 20 + 2)
        self.assertEqual(len(items_with_sections), 2)
        items_date_to = items.filtered(
            lambda x: x.date_to == fields.Date.to_date("2019-12-31")
        )
        self.assertEqual(len(items_date_to), 20)
        items_date_from = items.filtered(
            lambda x: x.date_from == fields.Date.to_date("2020-01-01")
        )
        self.assertEqual(len(items_date_from), 20)
        items_week_0 = items_without_sections.filtered(lambda x: x.week_type == "0")
        self.assertEqual(len(items_week_0), 10 + 10)
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-31")
                )
            ),
            5 + 5,
        )
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_from == fields.Date.to_date("2020-01-01")
                )
            ),
            5 + 5,
        )
        items_week_1 = items_without_sections.filtered(lambda x: x.week_type == "1")
        self.assertEqual(len(items_week_1), 10 + 10)
        self.assertEqual(
            len(
                items_week_1.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-31")
                )
            ),
            5 + 5,
        )
        self.assertEqual(
            len(
                items_week_1.filtered(
                    lambda x: x.date_from == fields.Date.to_date("2020-01-01")
                )
            ),
            5 + 5,
        )

    def test_calendar_planning_two_weeks_multi(self):
        self.calendar1.switch_calendar_type()
        self.calendar2.switch_calendar_type()
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id}),
            (
                0,
                0,
                {
                    "date_start": "2020-01-01",
                    "date_end": "2020-01-31",
                    "calendar_id": self.calendar2.id,
                },
            ),
            (
                0,
                0,
                {
                    "date_start": "2020-02-01",
                    "date_end": "2020-02-02",
                    "calendar_id": self.calendar1.id,
                },
            ),
            (0, 0, {"date_start": "2020-01-03", "calendar_id": self.calendar2.id}),
        ]
        items = self.employee.resource_calendar_id.attendance_ids
        items_with_sections = items.filtered(lambda x: x.display_type)
        items_without_sections = items - items_with_sections
        self.assertEqual(len(items), (20 * 2) + (20 * 2) + 2)
        self.assertEqual(len(items_with_sections), 2)
        items_week_0 = items_without_sections.filtered(lambda x: x.week_type == "0")
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2019-12-31")
                )
            ),
            10,
        )
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2020-01-31")
                )
            ),
            10,
        )
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_to == fields.Date.to_date("2020-02-02")
                )
            ),
            10,
        )
        self.assertEqual(
            len(
                items_week_0.filtered(
                    lambda x: x.date_from == fields.Date.to_date("2020-01-03")
                )
            ),
            10,
        )
        self.assertEqual(len(items_week_0), 20 + 20)
        items_week_1 = items_without_sections.filtered(lambda x: x.week_type == "1")
        self.assertEqual(len(items_week_0), len(items_week_1))

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
        # And that global leaves remain untouched
        self.assertEqual(
            self.calendar1.leave_ids, self.global_leave1 + self.global_leave2
        )
        self.assertTrue(
            self.leave1.id in self.employee.resource_calendar_id.leave_ids.ids
        )
        # Test that global leaves are copied to the autogenerated calendar on post install hook
        self.assertEqual(
            {
                global_leave.name
                for global_leave in self.employee.resource_calendar_id.global_leave_ids
            },
            {"Global Leave 1", "Global Leave 2"},
        )

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
            len(self.employee.calendar_ids[0].calendar_id.attendance_ids),
            2,
        )
        self.assertEqual(
            len(self.employee.calendar_ids[1].calendar_id.attendance_ids),
            8,
        )

    def test_resource_calendar_constraint(self):
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id})
        ]
        with self.assertRaises(exceptions.ValidationError):
            self.calendar1.write({"active": False})
        self.employee.write({"calendar_ids": [(2, self.employee.calendar_ids.id)]})
        self.calendar1.write({"active": False})
        self.assertFalse(self.calendar1.active)

    def test_resource_calendar_constraint_company_id(self):
        main_company = self.env.ref("base.main_company")
        self.calendar1.company_id = main_company
        self.employee.company_id = main_company
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2019-12-31", "calendar_id": self.calendar1.id})
        ]
        company2 = self.env["res.company"].create({"name": "Test company"})
        with self.assertRaises(exceptions.ValidationError):
            self.calendar1.company_id = company2

    def test_employee_with_calendar_ids(self):
        employee = self.env["hr.employee"].create(
            {
                "name": "Test employee",
                "calendar_ids": [
                    (
                        0,
                        0,
                        {"date_start": "2020-01-01", "calendar_id": self.calendar2.id},
                    ),
                ],
            }
        )
        self.assertTrue(employee.resource_calendar_id.auto_generate)

    def test_copy_global_leaves(self):
        # test that global leaves are combined from calendar_ids
        global_leave_ids_cal1 = self.calendar1.global_leave_ids.ids
        # self.employee.calendar_ids.unlink()
        self.employee.calendar_ids = [
            (0, 0, {"date_end": "2020-03-03", "calendar_id": self.calendar1.id}),
            (0, 0, {"date_start": "2020-03-03", "calendar_id": self.calendar2.id}),
        ]
        self.assertEqual(
            {
                global_leave.name
                for global_leave in self.employee.resource_calendar_id.global_leave_ids
            },
            {"Global Leave 1", "Global Leave 3"},
        )
        # test that global leaves on original calendar are not changed
        self.assertEqual(global_leave_ids_cal1, self.calendar1.global_leave_ids.ids)
