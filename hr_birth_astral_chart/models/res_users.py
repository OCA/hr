# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

from .astro_calc import calc_aspects, compute_chart
from .interpretations import build_daily_horoscope

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    astral_daily_horoscope = fields.Boolean(
        string="Daily Horoscope Notification",
        help="Show today's horoscope as a notification the first time you open "
        "Odoo each day. Needs a birth date and a birth time on your employee "
        "profile, and is only shown when a transit is currently active on your "
        "chart.",
    )
    astral_horoscope_last_date = fields.Date(
        string="Horoscope Last Shown",
        readonly=True,
        help="Technical field: last date this user was offered the daily "
        "horoscope notification.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["astral_daily_horoscope"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["astral_daily_horoscope"]

    @api.model
    def get_daily_horoscope(self):
        """Return today's horoscope for the current user, at most once a day.

        The return value is a ``{"title", "message"}`` dict the web client shows
        as a notification, or ``False`` when there is nothing to show: the
        option is off, the birth date or time is unknown, the horoscope was
        already offered today, or no transit is close enough to comment on.

        The birth time is required and never guessed: natal positions depend on
        it, the Moon by some 13 degrees over a single day, so aspects computed
        from an assumed hour would be made up. It is the ``birth_hour_known``
        flag that gates this, not a non-zero ``birth_hour``, so that a birth at
        midnight counts as known. Birth coordinates stay optional,
        as they only place the Ascendant and the houses, which this reading does
        not use.
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
        if not (employee.birthday and employee.birth_hour_known):
            return False
        # Marked before computing, so a chart is built at most once per user and
        # day even if the computation below fails.
        user.sudo().astral_horoscope_last_date = today
        lat = employee.birth_latitude or None
        lon = employee.birth_longitude or None
        if not (lat or lon):
            lat = lon = None
        try:
            natal = compute_chart(
                employee.birthday.year,
                employee.birthday.month,
                employee.birthday.day,
                hour=employee.birth_hour,
                lat=lat,
                lon=lon,
            )
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
