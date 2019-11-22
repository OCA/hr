# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision("Location")


class HrAttendanceLocation(models.Model):
    _name = "hr.attendance.location"
    _description = "HR Attendance Location"

    name = fields.Char()
    active = fields.Boolean(
        default=True,
    )
    latitude = fields.Float("Latitude", digits=UNIT)
    longitude = fields.Float("Latitude", digits=UNIT)
    allowed_radius = fields.Float(
        "Allowed range",
        default=lambda self: self.env.user.company_id.allowed_radius
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
