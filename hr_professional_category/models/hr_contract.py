# Copyright 2021 César Fernández Domínguez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    professional_category_id = fields.Many2one(
        comodel_name="hr.professional.category", string="Professional Category"
    )
