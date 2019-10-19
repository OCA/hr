# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import common


class TestHolidaysLeaveRepeated(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.date_start = datetime(2016, 12, 5, 8, 0, 0, 0)
        self.date_end = datetime(2016, 12, 5, 18, 0, 0, 0)

        self.calendar = self.env["resource.calendar"].create({"name": "Calendar 1"})

        for i in range(0, 7):
            self.env["resource.calendar.attendance"].create(
                {
                    "name": "Day " + str(i),
                    "dayofweek": str(i),
                    "hour_from": 8.0,
                    "hour_to": 16.0,
                    "calendar_id": self.calendar.id,
                }
            )

        self.employee_1 = self.env["hr.employee"].create(
            {"name": "Employee 1", "resource_calendar_id": self.calendar.id}
        )
        self.employee_2 = self.env["hr.employee"].create(
            {"name": "Employee 2", "resource_calendar_id": self.calendar.id}
        )
        self.employee_3 = self.env["hr.employee"].create(
            {"name": "Employee 3", "resource_calendar_id": self.calendar.id}
        )
        self.employee_4 = self.env["hr.employee"].create(
            {"name": "Employee 4", "resource_calendar_id": self.calendar.id}
        )
        self.employee_5 = self.env["hr.employee"].create(
            {"name": "Failing Employee", "resource_calendar_id": self.calendar.id}
        )

        self.status_1 = self.env["hr.leave.type"].create(
            {"name": "Repeating Status", "repeat": True, "validity_start": False}
        )

        self.leave_1 = self.env["hr.leave"].create(
            {
                "holiday_status_id": self.status_1.id,
                "holiday_type": "employee",
                "repeat_every": "workday",
                "repeat_mode": "times",
                "repeat_limit": 5,
                "date_from": self.date_start,
                "date_to": self.date_end,
                "employee_id": self.employee_1.id,
            }
        )
        self.leave_2 = self.env["hr.leave"].create(
            {
                "holiday_status_id": self.status_1.id,
                "holiday_type": "employee",
                "repeat_every": "week",
                "repeat_mode": "times",
                "repeat_limit": 4,
                "date_from": self.date_start,
                "date_to": self.date_end,
                "employee_id": self.employee_2.id,
            }
        )
        self.leave_3 = self.env["hr.leave"].create(
            {
                "holiday_status_id": self.status_1.id,
                "holiday_type": "employee",
                "repeat_every": "biweek",
                "repeat_mode": "times",
                "repeat_limit": 3,
                "date_from": self.date_start,
                "date_to": self.date_end,
                "employee_id": self.employee_3.id,
            }
        )
        self.leave_4 = self.env["hr.leave"].create(
            {
                "holiday_status_id": self.status_1.id,
                "holiday_type": "employee",
                "repeat_every": "month",
                "repeat_mode": "times",
                "repeat_limit": 2,
                "date_from": self.date_start,
                "date_to": self.date_end,
                "employee_id": self.employee_4.id,
            }
        )

    def test_01_count_repetitions(self):

        leave_1_list = self.env["hr.leave"].search(
            [
                ("holiday_status_id", "=", self.status_1.id),
                ("employee_id", "=", self.employee_1.id),
            ]
        )
        leave_2_list = self.env["hr.leave"].search(
            [
                ("holiday_status_id", "=", self.status_1.id),
                ("employee_id", "=", self.employee_2.id),
            ]
        )
        leave_3_list = self.env["hr.leave"].search(
            [
                ("holiday_status_id", "=", self.status_1.id),
                ("employee_id", "=", self.employee_3.id),
            ]
        )
        leave_4_list = self.env["hr.leave"].search(
            [
                ("holiday_status_id", "=", self.status_1.id),
                ("employee_id", "=", self.employee_4.id),
            ]
        )

        self.assertEqual(len(leave_1_list), 5)
        self.assertEqual(len(leave_2_list), 4)
        self.assertEqual(len(leave_3_list), 3)
        self.assertEqual(len(leave_4_list), 2)

    def test_02_workdays(self):
        for i in range(0, 5):
            check_from = self.date_start + timedelta(days=i)
            check_to = self.date_end + timedelta(days=i)
            leaves = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", self.status_1.id),
                    ("employee_id", "=", self.employee_1.id),
                    ("date_from", "=", check_from),
                    ("date_to", "=", check_to),
                ]
            )
            self.assertEqual(len(leaves), 1)

    def test_03_weeks(self):

        for i in range(0, 4):
            check_from = self.date_start + timedelta(days=i * 7)
            check_to = self.date_end + timedelta(days=i * 7)
            leaves = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", self.status_1.id),
                    ("employee_id", "=", self.employee_2.id),
                    ("date_from", "=", check_from),
                    ("date_to", "=", check_to),
                ]
            )
            self.assertEqual(len(leaves), 1)

    def test_04_biweeks(self):
        for i in range(0, 3):
            check_from = self.date_start + timedelta(days=i * 14)
            check_to = self.date_end + timedelta(days=i * 14)
            leaves = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", self.status_1.id),
                    ("employee_id", "=", self.employee_3.id),
                    ("date_from", "=", check_from),
                    ("date_to", "=", check_to),
                ]
            )
            self.assertEqual(len(leaves), 1)

    def test_05_months(self):
        for i in range(0, 2):
            check_from = self.date_start + timedelta(days=i * 28)
            check_to = self.date_end + timedelta(days=i * 28)
            leaves = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", self.status_1.id),
                    ("employee_id", "=", self.employee_4.id),
                    ("date_from", "=", check_from),
                    ("date_to", "=", check_to),
                ]
            )
            self.assertEqual(len(leaves), 1)

    def test_06_check_dates(self):
        with self.assertRaises(ValidationError):
            self.env["hr.leave"].create(
                {
                    "holiday_status_id": self.status_1.id,
                    "holiday_type": "employee",
                    "repeat_every": "workday",
                    "repeat_limit": -1,
                    "date_from": self.date_start,
                    "date_to": self.date_end,
                    "employee_id": self.employee_5.id,
                }
            )

    def test_07_check_dates(self):
        date_start = datetime(2019, 2, 18, 8, 0, 0, 0)
        date_end = datetime(2019, 2, 20, 18, 0, 0, 0)
        with self.assertRaises(UserError):
            self.env["hr.leave"].create(
                {
                    "holiday_status_id": self.status_1.id,
                    "holiday_type": "employee",
                    "repeat_every": "workday",
                    "repeat_mode": "times",
                    "repeat_limit": 5,
                    "date_from": date_start,
                    "date_to": date_end,
                    "employee_id": self.employee_5.id,
                }
            )

    def test_08_workdays_with_weekend(self):
        date_start = datetime(2019, 3, 1, 8, 0, 0, 0)
        date_end = datetime(2019, 3, 1, 18, 0, 0, 0)
        self.env["hr.leave"].create(
            {
                "holiday_status_id": self.status_1.id,
                "holiday_type": "employee",
                "repeat_every": "workday",
                "repeat_mode": "times",
                "repeat_limit": 5,
                "date_from": date_start,
                "date_to": date_end,
                "employee_id": self.employee_1.id,
            }
        )
        for i in range(0, 7):
            datetime_from = date_start + timedelta(days=i)
            datetime_to = date_end + timedelta(days=i)
            leaves = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", self.status_1.id),
                    ("employee_id", "=", self.employee_1.id),
                    ("date_from", "=", datetime_from),
                    ("date_to", "=", datetime_to),
                ]
            )
            if datetime_from.weekday() < 5:  # is a weekday
                self.assertEqual(len(leaves), 1)
            else:  # is weekend
                self.assertEqual(len(leaves), 0)

    def test_09_check_repeat_end_date(self):
        old_date = datetime(2019, 3, 18, 8, 0, 0, 0)
        date_start = datetime(2019, 2, 18, 8, 0, 0, 0)
        date_end = datetime(2019, 2, 18, 18, 0, 0, 0)
        with self.assertRaises(ValidationError):
            self.env["hr.leave"].create(
                {
                    "holiday_status_id": self.status_1.id,
                    "holiday_type": "employee",
                    "repeat_every": "workday",
                    "repeat_mode": "date",
                    "repeat_end_date": old_date,
                    "date_from": date_start,
                    "date_to": date_end,
                    "employee_id": self.employee_5.id,
                }
            )
