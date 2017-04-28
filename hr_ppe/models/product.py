# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ppe_ok = fields.Boolean(
        string='Can be PPE',
        help='Specify if the product can be selected as PPE')
