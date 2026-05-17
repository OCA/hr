# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from datetime import date, datetime
from unittest.mock import patch

import pytz

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user
from odoo.tools.translate import code_translations

from ..models.astro_calc import compute_chart, country_timezone, get_house, local_to_ut

BIRTHDAY = date(1985, 7, 14)
BIRTH_HOUR = 9.5
BCN_LAT, BCN_LON = 41.3874, 2.1686


class TestAstralChart(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.italy = cls.env.ref("base.it")
        cls.spain = cls.env.ref("base.es")

    def _employee(self, name="Chart Employee", user=None, **values):
        return self.env["hr.employee"].create(
            dict(
                {
                    "name": name,
                    "user_id": user.id if user else False,
                    "birthday": BIRTHDAY,
                },
                **values,
            )
        )

    def _full_employee(self, **values):
        return self._employee(
            birth_hour=BIRTH_HOUR,
            birth_hour_known=True,
            birth_latitude=BCN_LAT,
            birth_longitude=BCN_LON,
            **values,
        )

    # ── Time and place ────────────────────────────────────────────────────

    def test_the_birth_time_is_converted_to_universal_time(self):
        """Regression: local clock time fed in as UT put the Ascendant a sign out.

        09:30 in Barcelona is 07:30 UT, which gives Leo 26 degrees; the local
        09:30 taken as UT gave Virgo. The Ascendant moves about 15 degrees an
        hour, so the offset cannot be skipped.
        """
        zone = pytz.timezone("Europe/Madrid")
        self.assertEqual(
            local_to_ut(datetime(1985, 7, 14, 9, 30), zone), (1985, 7, 14, 7.5)
        )
        # Same clock time in winter, and one that rolls into the next day
        self.assertEqual(
            local_to_ut(datetime(1985, 1, 14, 9, 30), zone), (1985, 1, 14, 8.5)
        )
        self.assertEqual(
            local_to_ut(
                datetime(1990, 2, 3, 22, 15), pytz.timezone("America/New_York")
            ),
            (1990, 2, 4, 3.25),
        )
        employee = self._full_employee()
        self.assertAlmostEqual(
            employee._get_natal_chart()[0]["ascendant"], 146.102, places=2
        )
        self.assertIn("Leo", employee.birth_chart_rising_sign)

    def test_the_country_places_the_time_only_when_it_is_not_a_guess(self):
        """Italy is on one offset; Spain never is, thanks to the Canaries."""
        naive = datetime(1985, 7, 14, 9, 30)
        self.assertEqual(str(country_timezone("IT", naive)), "Europe/Rome")
        self.assertIsNone(country_timezone("ES", naive))
        self.assertIsNone(country_timezone("XX", naive))

        reference, _ = self._full_employee()._get_natal_chart()
        chart, time_exact = self._employee(
            name="Country Only",
            birth_hour=BIRTH_HOUR,
            birth_hour_known=True,
            country_of_birth=self.italy.id,
        )._get_natal_chart()
        self.assertTrue(time_exact)
        # Rome shares Barcelona's offset, so the bodies land on the same degrees
        self.assertAlmostEqual(
            chart["planets"]["moon"], reference["planets"]["moon"], places=6
        )
        # but a country is not a place, so there is still no Ascendant
        self.assertIsNone(chart["ascendant"])
        _chart, spanish_exact = self._employee(
            name="Spanish",
            birth_hour=BIRTH_HOUR,
            birth_hour_known=True,
            country_of_birth=self.spain.id,
        )._get_natal_chart()
        self.assertFalse(spanish_exact)

    def test_missing_data_degrades_instead_of_inventing(self):
        no_time = self._employee(birth_latitude=BCN_LAT, birth_longitude=BCN_LON)
        chart, time_exact = no_time._get_natal_chart()
        self.assertFalse(time_exact)
        self.assertIsNone(chart["ascendant"], "noon must not fake an Ascendant")
        self.assertFalse(no_time.birth_chart_exact)
        self.assertFalse(no_time.birth_chart_houses_html)

        undated = self.env["hr.employee"].create({"name": "Undated"})
        self.assertEqual(undated._get_natal_chart(), (None, False))
        self.assertFalse(undated.birth_chart_available)
        self.assertFalse(undated.birth_chart_svg)

    def test_whole_sign_houses_do_not_nail_the_midheaven_to_the_tenth(self):
        """Regression: the planet table used to hardcode house 10 for the MC."""
        chart = compute_chart(1985, 7, 14, hour=7.5, lat=64.1466, lon=-21.9426)
        for cusp in chart["houses"]:
            self.assertAlmostEqual(cusp % 30, 0.0, places=6)
        self.assertEqual(get_house(chart["ascendant"], chart["houses"]), 1)
        self.assertEqual(get_house(chart["midheaven"], chart["houses"]), 9)
        rows = json.loads(
            self._employee(
                name="Reykjavik",
                birth_hour=BIRTH_HOUR,
                birth_hour_known=True,
                birth_latitude=64.1466,
                birth_longitude=-21.9426,
            ).birth_chart_planets_json
        )
        midheaven = next(row for row in rows if row["key"] == "midheaven")
        self.assertEqual(midheaven["house"], 9)

    # ── What the form shows ───────────────────────────────────────────────

    def test_the_chart_fields_are_filled(self):
        employee = self._full_employee()
        self.assertTrue(employee.birth_chart_available)
        self.assertTrue(employee.birth_chart_exact)
        self.assertIn("<svg", employee.birth_chart_svg)
        self.assertIn("<svg", employee.birth_chart_transit_svg)
        self.assertIn("Cancer", employee.birth_chart_sun_sign)
        self.assertTrue(employee.birth_chart_interpretation)
        self.assertTrue(employee.birth_chart_houses_html)
        self.assertTrue(employee.birth_chart_transit_aspects)

        rows = json.loads(employee.birth_chart_planets_json)
        keys = [row["key"] for row in rows]
        self.assertEqual(len(keys), len(set(keys)), "the table needs unique t-keys")
        self.assertIn("ascendant", keys)
        for row in rows:
            self.assertTrue(row["name"])
            self.assertTrue(row["position"])

    def test_the_chart_is_rendered_in_the_reader_s_language(self):
        """Regression: the constant tables were unreachable for translators, and
        the computed fields were not keyed on the language either."""
        self.env["res.lang"]._activate_lang("es_ES")
        employee = self._full_employee()
        for name in ("birth_chart_sun_sign", "birth_chart_svg"):
            self.assertIn(
                "lang", self.env["hr.employee"]._fields[name]._depends_context, name
            )
        fake = {"Cancer": "Cáncer", "Sun": "Sol", "Leo": "León"}
        with patch.dict(
            code_translations.python_translations,
            {("hr_birth_astral_chart", "es_ES"): fake},
        ):
            spanish = employee.with_context(lang="es_ES")
            self.assertIn("Cáncer", spanish.birth_chart_sun_sign)
            self.assertIn("León", spanish.birth_chart_rising_sign)
            names = [
                row["name"] for row in json.loads(spanish.birth_chart_planets_json)
            ]
            self.assertIn("Sol", names)
            self.assertIn(
                "Cancer", employee.with_context(lang="en_US").birth_chart_sun_sign
            )

    # ── The daily notification ────────────────────────────────────────────

    def test_the_daily_horoscope_is_offered_once_a_day(self):
        user = new_test_user(
            self.env, login="astro_user", groups="base.group_user", tz="Europe/Madrid"
        )
        user.astral_daily_horoscope = True
        employee = self._full_employee(user=user)
        Users = self.env["res.users"].with_user(user)

        first = Users.get_daily_horoscope()
        self.assertTrue(first["message"])
        self.assertTrue(first["title"])
        self.assertFalse(Users.get_daily_horoscope(), "twice a day is once too many")

        user.astral_horoscope_last_date = date(2020, 1, 1)
        self.assertTrue(Users.get_daily_horoscope())

        user.astral_horoscope_last_date = False
        user.astral_daily_horoscope = False
        self.assertFalse(Users.get_daily_horoscope())
        self.assertFalse(
            user.astral_horoscope_last_date, "an untouched day must not be spent"
        )

        user.astral_daily_horoscope = True
        employee.write({"birth_hour": 0.0, "birth_hour_known": False})
        self.assertFalse(Users.get_daily_horoscope(), "an unknown time is no reading")

    def test_the_horoscope_day_follows_the_user_s_own_timezone(self):
        """Two users either side of the date line are not on the same day."""
        last_dates = []
        for login, tz in (("east", "Pacific/Kiritimati"), ("west", "Pacific/Midway")):
            user = new_test_user(self.env, login=login, groups="base.group_user", tz=tz)
            user.astral_daily_horoscope = True
            self._full_employee(name=login, user=user)
            self.env["res.users"].with_user(user).get_daily_horoscope()
            last_dates.append(user.astral_horoscope_last_date)
        self.assertNotEqual(*last_dates)

    # ── What an employee may see ──────────────────────────────────────────

    def test_an_employee_sees_their_own_chart_and_nobody_else_s(self):
        """Regression: res.users is readable by every internal user, so a
        colleague's sun sign was one read away, and with it their birth date."""
        ann = new_test_user(self.env, login="ann", groups="base.group_user")
        bob = new_test_user(self.env, login="bob", groups="base.group_user")
        self._full_employee(name="Ann", user=ann)
        self._full_employee(name="Bob", user=bob, birthday=date(1972, 12, 3))

        with self.assertRaises(AccessError):
            self.env["hr.employee"].with_user(ann).search([]).mapped("birthday")

        mine = self.env["res.users"].with_user(ann).browse(ann.id)
        self.assertTrue(mine.birth_chart_available)
        self.assertIn("Cancer", mine.birth_chart_sun_sign)
        self.assertIn("<svg", mine.birth_chart_svg)

        theirs = self.env["res.users"].with_user(ann).browse(bob.id)
        self.assertFalse(theirs.birth_chart_sun_sign)
        self.assertFalse(theirs.birth_chart_available)
        for name in ("birth_chart_sun_sign", "birth_chart_available"):
            self.assertIn(
                "uid", self.env["res.users"]._fields[name]._depends_context, name
            )

        action = self.env["res.users"].with_user(ann).env.user._action_my_astral_chart()
        self.assertEqual(action["res_id"], ann.id)
