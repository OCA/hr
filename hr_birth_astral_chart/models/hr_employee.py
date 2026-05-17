# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from datetime import date as date_type

from odoo import api, fields, models

from .astro_calc import SIGN_SYMBOLS, SIGNS, calc_aspects, compute_chart, lon_to_sign
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
        sanitize=False,
    )
    birth_chart_planets_json = fields.Char(
        compute="_compute_birth_chart",
    )
    birth_chart_sun_sign = fields.Char(
        string="Sun Sign",
        compute="_compute_birth_chart",
    )
    birth_chart_moon_sign = fields.Char(
        string="Moon Sign",
        compute="_compute_birth_chart",
    )
    birth_chart_rising_sign = fields.Char(
        string="Ascendant",
        compute="_compute_birth_chart",
    )
    birth_chart_available = fields.Boolean(
        compute="_compute_birth_chart",
    )
    birth_chart_interpretation = fields.Html(
        string="Chart Interpretation",
        compute="_compute_birth_chart",
        sanitize=False,
    )
    birth_chart_houses_html = fields.Html(
        string="Houses",
        compute="_compute_birth_chart",
        sanitize=False,
    )

    # ── Transit chart (recomputes on every page load — not stored) ────────────
    birth_chart_transit_svg = fields.Html(
        string="Transit Chart",
        compute="_compute_transit_chart",
        sanitize=False,
    )
    birth_chart_transit_json = fields.Char(
        compute="_compute_transit_chart",
    )
    birth_chart_transit_aspects = fields.Html(
        string="Transit Aspects",
        compute="_compute_transit_chart",
        sanitize=False,
    )
    birth_chart_transit_interpretation = fields.Html(
        string="Transit Interpretation",
        compute="_compute_transit_chart",
        sanitize=False,
    )

    @api.depends(
        "birthday",
        "birth_hour",
        "birth_hour_known",
        "birth_latitude",
        "birth_longitude",
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
                continue

            bd = rec.birthday
            lat = rec.birth_latitude or None
            lon = rec.birth_longitude or None
            if not (lat or lon):
                lat = lon = None

            chart = compute_chart(
                bd.year,
                bd.month,
                bd.day,
                hour=rec.birth_hour if rec.birth_hour_known else 12.0,
                lat=lat,
                lon=lon,
            )

            rec.birth_chart_svg = generate_chart_svg(chart)
            rec.birth_chart_available = True

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

            bd = rec.birthday
            lat = rec.birth_latitude or None
            lon = rec.birth_longitude or None
            if not (lat or lon):
                lat = lon = None

            natal = compute_chart(
                bd.year,
                bd.month,
                bd.day,
                hour=rec.birth_hour if rec.birth_hour_known else 12.0,
                lat=lat,
                lon=lon,
            )
            aspects = calc_aspects(natal["planets"], transit["planets"])
            rec.birth_chart_transit_svg = generate_biwheel_svg(natal, transit, aspects)
            rows, _extra = build_planet_table(self.env, transit)
            rec.birth_chart_transit_json = json.dumps(rows)
            aspects_html, interp_html = build_transit_interpretation(
                self.env, natal, transit, aspects, today
            )
            rec.birth_chart_transit_aspects = aspects_html or False
            rec.birth_chart_transit_interpretation = interp_html or False
