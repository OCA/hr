# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    is_personal_equipment = fields.Boolean(default=False,
                                           string="Is Employee Personal Equipment")
