###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    internal_equipment = fields.Boolean(
        string='Internal equipment',
    )
    information = fields.Text(
        string='Information',
    )
    item_count = fields.Integer(
        string='Items',
        compute='_compute_item_count',
    )

    def _compute_item_count(self):
        for rec in self:
            rec.item_count = self.env['workspace.item'].search(
                [('product_id', '=', rec.id)],
                count=True,
            )

    def product_item_count(self):
        return{
            'name': 'Items',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'workspace.item',
            'type': 'ir.actions.act_window',
            'context': {'default_product_id': self.id},
            'domain': [('product_id', '=', self.id)],
        }
