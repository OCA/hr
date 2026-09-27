# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birth_hour = fields.Float(
        string="Birth Time",
        help="Birth time in decimal hours (e.g. 14.5 = 14:30). "
        "Required to compute the Ascendant and Houses.",
    )
    birth_hour_known = fields.Boolean(
        string="Birth Time Known",
        compute="_compute_birth_hour_known",
        store=True,
        readonly=False,
        help="Whether the birth time is real data. A float column cannot tell "
        "midnight from an empty value, so entering any time other than 00:00 "
        "ticks this automatically, and someone actually born at midnight has "
        "to confirm it by hand.",
    )
    birth_latitude = fields.Float(
        digits=(10, 6),
        help="Geographic latitude of birth place (+ north, − south).",
    )
    birth_longitude = fields.Float(
        digits=(10, 6),
        help="Geographic longitude of birth place (+ east, − west).",
    )
    birth_location_known = fields.Boolean(
        compute="_compute_birth_location_known",
    )

    _check_birth_hour = models.Constraint(
        "CHECK(birth_hour >= 0 AND birth_hour < 24)",
        "The birth time must be a decimal hour between 0 and 24 (24 excluded).",
    )
    _check_birth_latitude = models.Constraint(
        "CHECK(birth_latitude >= -90 AND birth_latitude <= 90)",
        "The birth latitude must be between -90 and 90 degrees.",
    )
    _check_birth_longitude = models.Constraint(
        "CHECK(birth_longitude >= -180 AND birth_longitude <= 180)",
        "The birth longitude must be between -180 and 180 degrees.",
    )

    @api.depends("birth_hour")
    def _compute_birth_hour_known(self):
        """Any time other than midnight is known data by definition.

        The field is stored and writable, so an explicit value written together
        with the birth time wins over this default: that is how a birth at
        00:00 is told apart from an unknown time.
        """
        for rec in self:
            rec.birth_hour_known = bool(rec.birth_hour)

    @api.depends("birth_latitude", "birth_longitude")
    def _compute_birth_location_known(self):
        for rec in self:
            rec.birth_location_known = bool(rec.birth_latitude or rec.birth_longitude)
