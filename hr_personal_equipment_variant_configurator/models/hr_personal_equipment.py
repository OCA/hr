# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrPersonalEquipment(models.Model):

    _inherit = ["hr.personal.equipment", "product.configurator"]
    _name = "hr.personal.equipment"

    product_tmpl_id = fields.Many2one(domain=[("is_personal_equipment", "=", True)])
