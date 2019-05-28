# Copyright <2019> <BerrySoft MX>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    # Anniversaries fields
    employment_anniversary = fields.Date()
