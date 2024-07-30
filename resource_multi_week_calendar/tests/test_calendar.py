# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCalendarConstraints(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Calendar = cls.env["resource.calendar"]
        cls.parent_calendar = cls.Calendar.create({"name": "Parent"})

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


class TestCalendarWeekNumber(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Calendar = cls.env["resource.calendar"]
        cls.parent_calendar = cls.Calendar.create({"name": "Parent"})

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
