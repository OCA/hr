# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class CalendarCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Calendar = cls.env["resource.calendar"]
        cls.parent_calendar = cls.Calendar.create({"name": "Parent"})
        cls._sequence = 0

    def create_simple_child(self):
        self._sequence += 1
        return self.Calendar.create(
            {
                "name": "Child {}".format(self._sequence),
                "parent_calendar_id": self.parent_calendar.id,
                "week_sequence": self._sequence,
            }
        )


class TestCalendarConstraints(CalendarCase):
    def test_cant_add_child_to_child(self):
        one = self.Calendar.create(
            {
                "name": "One",
                "parent_calendar_id": self.parent_calendar.id,
                "week_sequence": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.Calendar.create(
                {
                    "name": "Two",
                    "parent_calendar_id": one.id,
                    "week_sequence": 2,
                }
            )

    def test_cant_add_parent_to_parent(self):
        self.Calendar.create(
            {
                "name": "Child",
                "parent_calendar_id": self.parent_calendar.id,
                "week_sequence": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.Calendar.create(
                {
                    "name": "Parent of parent",
                    "child_calendar_ids": self.parent_calendar.ids,
                    # This value is kind of arbitrary here.
                    "week_sequence": 2,
                }
            )

    def test_cant_change_epoch_date(self):
        child = self.create_simple_child()
        with self.assertRaises(ValidationError):
            child.multi_week_epoch_date = "2001-01-01"


class TestCalendarIsMultiweek(CalendarCase):
    def test_solo(self):
        self.assertFalse(self.parent_calendar.is_multi_week)

    def test_has_child_or_parent(self):
        child = self.create_simple_child()
        self.assertTrue(self.parent_calendar.is_multi_week)
        self.assertTrue(child.is_multi_week)


class TestCalendarWeekNumber(CalendarCase):
    def test_solo(self):
        self.assertEqual(self.parent_calendar.week_number, 1)

    def test_children(self):
        # The parent's sequence should not matter.
        self.parent_calendar.week_sequence = 100
        one = self.Calendar.create(
            {
                "name": "One",
                "parent_calendar_id": self.parent_calendar.id,
                "week_sequence": 1,
            }
        )
        two = self.Calendar.create(
            {
                "name": "Two",
                "parent_calendar_id": self.parent_calendar.id,
                # Arbitrarily big number.
                "week_sequence": 30,
            }
        )
        self.assertEqual(self.parent_calendar.week_number, 1)
        self.assertEqual(one.week_number, 2)
        self.assertEqual(two.week_number, 3)

        # Change the order.
        one.week_sequence = 31
        self.assertEqual(one.week_number, 3)
        self.assertEqual(two.week_number, 2)


class TestCalendarWeekEpoch(CalendarCase):
    def test_set_epoch_on_parent(self):
        child = self.create_simple_child()
        self.parent_calendar.multi_week_epoch_date = "2001-01-01"
        self.assertEqual(child.multi_week_epoch_date, datetime.date(2001, 1, 1))

    def test_set_epoch_on_parent_prior_to_creation(self):
        self.parent_calendar.multi_week_epoch_date = "2001-01-01"
        child = self.create_simple_child()
        self.assertEqual(child.multi_week_epoch_date, datetime.date(2001, 1, 1))

    def test_unix_epoch_default(self):
        self.assertEqual(
            self.parent_calendar.multi_week_epoch_date, datetime.date(1970, 1, 1)
        )

    @freeze_time("1970-01-08")
    def test_compute_current_week_no_family(self):
        self.assertEqual(self.parent_calendar.current_week_number, 1)
        self.assertEqual(self.parent_calendar.current_calendar_id, self.parent_calendar)

    @freeze_time("1970-01-01")
    def test_compute_current_week_same_day(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 1)
        self.assertEqual(child.current_calendar_id, self.parent_calendar)

    # 1969-12-29 is a Monday.
    @freeze_time("1969-12-29")
    def test_compute_current_week_first_day_of_week(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 1)
        self.assertEqual(child.current_calendar_id, self.parent_calendar)

    # 1969-12-28 is a Sunday.
    @freeze_time("1969-12-28")
    def test_compute_current_week_one_week_ago(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 2)
        self.assertEqual(child.current_calendar_id, child)
        # Test against parent, too, which should have the same result.
        self.assertEqual(self.parent_calendar.current_week_number, 2)
        self.assertEqual(self.parent_calendar.current_calendar_id, child)

    # 1970-01-04 is a Sunday.
    @freeze_time("1970-01-04")
    def test_compute_current_week_last_day_of_week(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 1)
        self.assertEqual(child.current_calendar_id, self.parent_calendar)

    # 1970-01-05 is a Monday.
    @freeze_time("1970-01-05")
    def test_compute_current_week_next_week(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 2)
        self.assertEqual(child.current_calendar_id, child)

    # 1970-01-12 is a Monday.
    @freeze_time("1970-01-12")
    def test_compute_current_week_in_two_weeks(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 1)
        self.assertEqual(child.current_calendar_id, self.parent_calendar)

    # 1970-01-12 is a Monday.
    @freeze_time("1970-01-12")
    def test_compute_current_week_in_two_weeks_three_calendars(self):
        self.create_simple_child()
        child_2 = self.create_simple_child()
        self.assertEqual(child_2.current_week_number, 3)
        self.assertEqual(child_2.current_calendar_id, child_2)

    # 1970-01-04 is a Sunday.
    @freeze_time("1970-01-04")
    def test_compute_current_week_when_day_changes(self):
        child = self.create_simple_child()
        self.assertEqual(child.current_week_number, 1)
        self.assertEqual(child.current_calendar_id, self.parent_calendar)
        with freeze_time("1970-01-05"):
            # This re-compute shouldn't technically be needed... Maybe there's a
            # cache?
            child._compute_current_week()
            self.assertEqual(child.current_week_number, 2)
            self.assertEqual(child.current_calendar_id, child)
