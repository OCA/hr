# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

from .astro_calc import calc_aspects, compute_chart
from .interpretations import build_daily_horoscope

_logger = logging.getLogger(__name__)

# hr.employee is only reachable by HR users, so an employee cannot read the
# chart on their own employee record. These fields mirror it onto res.users,
# which every internal user can read, so _compute_astral_chart fills them for
# the asking user only.
ASTRAL_CHART_FIELDS = [
    "birth_chart_available",
    "birth_chart_exact",
    "birth_chart_svg",
    "birth_chart_planets_json",
    "birth_chart_sun_sign",
    "birth_chart_moon_sign",
    "birth_chart_rising_sign",
    "birth_chart_interpretation",
    "birth_chart_houses_html",
    "birth_chart_transit_svg",
    "birth_chart_transit_json",
    "birth_chart_transit_aspects",
    "birth_chart_transit_interpretation",
]


class ResUsers(models.Model):
    _inherit = "res.users"

    astral_daily_horoscope = fields.Boolean(
        string="Daily Horoscope Notification",
        help="Show today's horoscope as a notification the first time you open "
        "Odoo each day. Needs a birth date and a birth time on your employee "
        "profile, plus either birth coordinates or a country of birth to place "
        "that time, and is only shown when a transit is currently active on "
        "your chart.",
    )
    astral_horoscope_last_date = fields.Date(
        string="Horoscope Last Shown",
        readonly=True,
        help="Technical field: last date this user was offered the daily "
        "horoscope notification.",
    )

    birth_chart_available = fields.Boolean(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_exact = fields.Boolean(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_svg = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )
    birth_chart_planets_json = fields.Char(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_sun_sign = fields.Char(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_moon_sign = fields.Char(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_rising_sign = fields.Char(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_interpretation = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )
    birth_chart_houses_html = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )
    birth_chart_transit_svg = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )
    birth_chart_transit_json = fields.Char(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
    )
    birth_chart_transit_aspects = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )
    birth_chart_transit_interpretation = fields.Html(
        compute="_compute_astral_chart",
        depends_context=("uid", "lang"),
        sanitize=False,
    )

    @api.depends(
        "employee_id.birthday",
        "employee_id.birth_hour",
        "employee_id.birth_hour_known",
        "employee_id.birth_latitude",
        "employee_id.birth_longitude",
        "employee_id.country_of_birth",
    )
    def _compute_astral_chart(self):
        """Mirror the employee's chart, but only onto the user who is asking.

        These fields exist so an employee can reach their own chart without
        access to hr.employee, so they stay empty on anybody else's record. That
        is not belt and braces: res.users is readable by every internal user,
        and SELF_READABLE_FIELDS grants access rather than restricting it, so
        without this check a colleague's sun sign would be one read away, and
        with it their birth date, which Odoo keeps for HR users only.
        """
        empty = self.env["hr.employee"]
        for user in self:
            # sudo: hr.employee is out of reach for the employee themselves
            employee = user.sudo().employee_id if user.id == self.env.uid else empty
            for name in ASTRAL_CHART_FIELDS:
                user[name] = employee[name] if employee else False

    @property
    def SELF_READABLE_FIELDS(self):
        return (
            super().SELF_READABLE_FIELDS
            + ["astral_daily_horoscope"]
            + ASTRAL_CHART_FIELDS
        )

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["astral_daily_horoscope"]

    def _action_my_astral_chart(self):
        """Open the current user's own chart.

        Employees have no access to hr.employee, so their chart is reached on
        their own res.users record instead of the employee form.
        """
        view = self.env.ref("hr_birth_astral_chart.res_users_view_form_astral_chart")
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("My Astral Chart"),
            "res_model": "res.users",
            "res_id": self.env.uid,
            "views": [(view.id, "form")],
            "target": "current",
        }

    @api.model
    def get_daily_horoscope(self):
        """Return today's horoscope for the current user, at most once a day.

        The return value is a ``{"title", "message"}`` dict the web client shows
        as a notification, or ``False`` when there is nothing to show: the
        option is off, the birth date or time is unknown, the birth timezone
        cannot be resolved, the horoscope was already offered today, or no
        transit is close enough to comment on.

        The birth time is required and never guessed: natal positions depend on
        it, the Moon by some 13 degrees over a single day, so aspects computed
        from an assumed hour would be made up. It is the ``birth_hour_known``
        flag that gates it, not a non-zero ``birth_hour``, so that a birth at
        midnight counts as known.

        A birth time is local clock time, so its timezone has to be resolvable
        as well, from the coordinates or else from the country of birth. The
        coordinates themselves are not needed here: they place the Ascendant
        and the houses, which this reading does not use.
        """
        user = self.env.user
        if not user.astral_daily_horoscope:
            return False
        # Answer in the language and on the day of the user being answered,
        # rather than trusting the caller's context: env.lang only reads the
        # context, it does not fall back to the user's own language.
        user = user.with_context(lang=user.lang or "en_US", tz=user.tz)
        env = user.env
        today = fields.Date.context_today(user)
        if user.astral_horoscope_last_date == today:
            return False
        employee = user.employee_id.sudo()
        if not employee.birthday:
            return False
        # Marked before computing, so a chart is built at most once per user and
        # day even if the computation below fails.
        user.sudo().astral_horoscope_last_date = today
        try:
            natal, time_exact = employee._get_natal_chart()
            if not time_exact:
                return False
            transit = compute_chart(today.year, today.month, today.day, hour=12.0)
            message = build_daily_horoscope(
                env, calc_aspects(natal["planets"], transit["planets"])
            )
        except Exception:
            _logger.exception(
                "Could not compute the daily horoscope of user %s", user.login
            )
            return False
        if not message:
            return False
        return {"title": env._("Your horoscope for today"), "message": message}
