# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float(
        string="Check-in Latitude", digits="Location", readonly=True
    )
    check_in_longitude = fields.Float(
        string="Check-in Longitude", digits="Location", readonly=True
    )
    check_out_latitude = fields.Float(
        string="Check-out Latitude", digits="Location", readonly=True
    )
    check_out_longitude = fields.Float(
        string="Check-out Longitude", digits="Location", readonly=True
    )
