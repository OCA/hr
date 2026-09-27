# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from datetime import date as date_type
from datetime import datetime, timedelta

from odoo import api, fields, models

from .astro_calc import (
    SIGN_SYMBOLS,
    SIGNS,
    calc_aspects,
    compute_chart,
    country_timezone,
    local_to_ut,
    lon_to_sign,
    timezone_at,
)
from .chart_svg import (
    build_houses_html,
    build_planet_table,
    generate_biwheel_svg,
    generate_chart_svg,
)
from .interpretations import build_interpretation, build_transit_interpretation


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # ── Computed chart fields ─────────────────────────────────────────────
    birth_chart_svg = fields.Html(
        string="Birth Chart",
        compute="_compute_birth_chart",
        depends_context=("lang",),
        sanitize=False,
    )
    birth_chart_planets_json = fields.Char(
        compute="_compute_birth_chart",
        depends_context=("lang",),
    )
    birth_chart_sun_sign = fields.Char(
        string="Sun Sign",
        compute="_compute_birth_chart",
        depends_context=("lang",),
    )
    birth_chart_moon_sign = fields.Char(
        string="Moon Sign",
        compute="_compute_birth_chart",
        depends_context=("lang",),
    )
    birth_chart_rising_sign = fields.Char(
        string="Ascendant",
        compute="_compute_birth_chart",
        depends_context=("lang",),
    )
    birth_chart_available = fields.Boolean(
        compute="_compute_birth_chart",
        depends_context=("lang",),
    )
    birth_chart_exact = fields.Boolean(
        string="Ascendant Available",
        compute="_compute_birth_chart",
        depends_context=("lang",),
        help="The birth time and the coordinates are both known, so the "
        "Ascendant and the houses are real rather than assumed.",
    )
    birth_chart_interpretation = fields.Html(
        string="Chart Interpretation",
        compute="_compute_birth_chart",
        depends_context=("lang",),
        sanitize=False,
    )
    birth_chart_houses_html = fields.Html(
        string="Houses",
        compute="_compute_birth_chart",
        depends_context=("lang",),
        sanitize=False,
    )

    # ── Transit chart (recomputes on every page load — not stored) ────────────
    birth_chart_transit_svg = fields.Html(
        string="Transit Chart",
        compute="_compute_transit_chart",
        depends_context=("lang",),
        sanitize=False,
    )
    birth_chart_transit_json = fields.Char(
        compute="_compute_transit_chart",
        depends_context=("lang",),
    )
    birth_chart_transit_aspects = fields.Html(
        string="Transit Aspects",
        compute="_compute_transit_chart",
        depends_context=("lang",),
        sanitize=False,
    )
    birth_chart_transit_interpretation = fields.Html(
        string="Transit Interpretation",
        compute="_compute_transit_chart",
        depends_context=("lang",),
        sanitize=False,
    )

    def _get_birth_timezone(self, naive):
        """Return the timezone the birth time was recorded in, or None.

        The coordinates settle it outright. Failing those, the country of birth
        can still settle it whenever every zone that country uses was on the
        same offset that day, which is enough to place the planets even though
        the Ascendant will stay unknown for want of real coordinates.
        """
        self.ensure_one()
        if self.birth_location_known:
            return timezone_at(self.birth_latitude, self.birth_longitude)
        country_code = self.country_of_birth.code
        return country_timezone(country_code, naive) if country_code else None

    def _get_natal_chart(self):
        """Return ``(chart, time_exact)``, or ``(None, False)`` without a date.

        ``time_exact`` is True when the birth time was known and its timezone
        could be resolved, so the chart sits on the right instant of Universal
        Time. Otherwise the chart falls back to noon UT: the slow bodies still
        land correctly, but the Moon can be some 6 degrees out.

        The coordinates are only handed to the ephemeris when they are known,
        since they are what places the Ascendant and the houses. So a birth with
        a resolved time but no coordinates gives exact planets and no Ascendant,
        which is what ``chart["ascendant"] is None`` then reports.
        """
        self.ensure_one()
        if not self.birthday:
            return None, False
        bd = self.birthday
        if self.birth_hour_known:
            naive = datetime(bd.year, bd.month, bd.day) + timedelta(
                hours=self.birth_hour
            )
            zone = self._get_birth_timezone(naive)
            if zone is not None:
                lat = self.birth_latitude if self.birth_location_known else None
                lon = self.birth_longitude if self.birth_location_known else None
                return compute_chart(*local_to_ut(naive, zone), lat=lat, lon=lon), True
        return compute_chart(bd.year, bd.month, bd.day, hour=12.0), False

    @api.depends(
        "birthday",
        "birth_hour",
        "birth_hour_known",
        "birth_latitude",
        "birth_longitude",
        "country_of_birth",
    )
    def _compute_birth_chart(self):
        for rec in self:
            if not rec.birthday:
                rec.birth_chart_svg = False
                rec.birth_chart_planets_json = False
                rec.birth_chart_sun_sign = False
                rec.birth_chart_moon_sign = False
                rec.birth_chart_rising_sign = False
                rec.birth_chart_interpretation = False
                rec.birth_chart_houses_html = False
                rec.birth_chart_available = False
                rec.birth_chart_exact = False
                continue

            chart, _time_exact = rec._get_natal_chart()

            rec.birth_chart_svg = generate_chart_svg(chart)
            rec.birth_chart_available = True
            rec.birth_chart_exact = chart["ascendant"] is not None

            sun_i, sun_d, sun_m = lon_to_sign(chart["planets"]["sun"])
            moon_i, moon_d, moon_m = lon_to_sign(chart["planets"]["moon"])
            rec.birth_chart_sun_sign = (
                f"{SIGN_SYMBOLS[sun_i]} {self.env._(SIGNS[sun_i])} {sun_d}° {sun_m}'"
            )
            rec.birth_chart_moon_sign = (
                f"{SIGN_SYMBOLS[moon_i]}"
                f" {self.env._(SIGNS[moon_i])} {moon_d}° {moon_m}'"
            )

            if chart["ascendant"] is not None:
                asc_i, asc_d, asc_m = lon_to_sign(chart["ascendant"])
                rec.birth_chart_rising_sign = (
                    f"{SIGN_SYMBOLS[asc_i]}"
                    f" {self.env._(SIGNS[asc_i])} {asc_d}° {asc_m}'"
                )
            else:
                rec.birth_chart_rising_sign = self.env._(
                    "Requires birth time and location"
                )

            rows, extra = build_planet_table(self.env, chart)
            rec.birth_chart_planets_json = json.dumps(rows + extra)
            rec.birth_chart_interpretation = build_interpretation(self.env, chart)
            rec.birth_chart_houses_html = build_houses_html(self.env, chart) or False

    @api.depends(
        "birthday",
        "birth_hour",
        "birth_hour_known",
        "birth_latitude",
        "birth_longitude",
        "country_of_birth",
    )
    def _compute_transit_chart(self):
        today = date_type.today()
        transit = compute_chart(today.year, today.month, today.day, hour=12.0)
        for rec in self:
            if not rec.birthday:
                rec.birth_chart_transit_svg = False
                rec.birth_chart_transit_json = False
                rec.birth_chart_transit_aspects = False
                rec.birth_chart_transit_interpretation = False
                continue

            natal, _exact = rec._get_natal_chart()
            aspects = calc_aspects(natal["planets"], transit["planets"])
            rec.birth_chart_transit_svg = generate_biwheel_svg(natal, transit, aspects)
            rows, _extra = build_planet_table(self.env, transit)
            rec.birth_chart_transit_json = json.dumps(rows)
            aspects_html, interp_html = build_transit_interpretation(
                self.env, natal, transit, aspects, today
            )
            rec.birth_chart_transit_aspects = aspects_html or False
            rec.birth_chart_transit_interpretation = interp_html or False
