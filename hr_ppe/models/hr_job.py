# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class HrJob(models.Model):
    _inherit = 'hr.job'

    ppe_ids = fields.One2many(
        string='PPEs', comodel_name='hr.job.ppe', inverse_name='job_id')


class HrJobPpe(models.Model):
    _name = 'hr.job.ppe'

    job_id = fields.Many2one(
        string='Job Title', comodel_name='hr.job', required=True)
    product_id = fields.Many2one(
        string='Product', comodel_name='product.product', required=True,
        domain="[('ppe_ok', '=', True)]")
    product_uom_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1.0)
    product_uom_id = fields.Many2one(
        string='Unit of Measure', comodel_name='product.uom', required=True)

    _sql_constraints = [
        ('product_uom_qty', ' CHECK (product_uom_qty > 0.0)',
         'Product quantity must be positive!'),
    ]

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id
