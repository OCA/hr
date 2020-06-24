# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployeePpeEquipment(models.Model):

    _name = 'hr.employee.ppe.equipment'
    _description = 'Personal Protective Equipments - Equipment List'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        required=True,
        help="""Select the PPE from the product list.
            Please note that the PPE must be a consumable product.""",
        comodel_name='product.product',
        domain="[('type', '=', 'consu')]"
    )
    expirable = fields.Boolean(
        help='Select this option if the PPE has expiry date.'
    )

    @api.onchange('product_id')
    def update_name(self):
        self.name = self.product_id.name
