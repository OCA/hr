# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision("Location")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float(
        "Check-in Latitude",
        digits=UNIT,
        readonly=True
    )
    check_in_longitude = fields.Float(
        "Check-in Longitude",
        digits=UNIT,
        readonly=True
    )
    check_out_latitude = fields.Float(
        "Check-out Latitude",
        digits=UNIT,
        readonly=True
    )
    check_out_longitude = fields.Float(
        "Check-out Longitude",
        digits=UNIT,
        readonly=True
    )
