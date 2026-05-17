# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import psycopg2

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestBirthData(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})

    def _assert_rejected(self, values):
        """A database CHECK fires on flush, so it needs its own savepoint."""
        with self.assertRaises(psycopg2.IntegrityError), mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                self.employee.write(values)
                self.env.flush_all()

    def test_the_ranges_accept_valid_data(self):
        self.employee.write(
            {"birth_hour": 23.99, "birth_latitude": -90.0, "birth_longitude": 180.0}
        )
        self.env.flush_all()
        self.assertEqual(self.employee.birth_hour, 23.99)
        # Unset coordinates are NULL, which must not trip the CHECK either
        blank = self.env["hr.employee"].create({"name": "No Coordinates"})
        self.env.flush_all()
        self.assertFalse(blank.birth_latitude)

    def test_the_ranges_reject_invalid_data(self):
        self._assert_rejected({"birth_hour": 24.0})
        self._assert_rejected({"birth_hour": -0.5})
        self._assert_rejected({"birth_latitude": 90.5})
        self._assert_rejected({"birth_longitude": -180.1})

    def test_a_real_time_marks_itself_known(self):
        self.assertFalse(self.employee.birth_hour_known)
        self.employee.birth_hour = 9.5
        self.assertTrue(self.employee.birth_hour_known)
        self.employee.birth_hour = 0.0
        self.assertFalse(self.employee.birth_hour_known)

    def test_midnight_can_be_told_from_an_unknown_time(self):
        """A float column cannot, so the explicit flag has to win and stick."""
        self.employee.write({"birth_hour": 0.0, "birth_hour_known": True})
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertTrue(self.employee.birth_hour_known)

    def test_birth_location_known(self):
        self.assertFalse(self.employee.birth_location_known)
        self.employee.birth_latitude = 41.3874
        self.assertTrue(self.employee.birth_location_known)
