# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    identification_type_id = fields.Many2one(
        "hr.employee.identification.type", groups="hr.group_hr_user"
    )
    identification_expiry_date = fields.Date(
        "Identification expiry", groups="hr.group_hr_user"
    )
