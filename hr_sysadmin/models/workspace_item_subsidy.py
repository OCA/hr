###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class WorkspaceItemSubsidy(models.Model):
    _name = 'workspace.item.subsidy'
    _inherit = 'mail.thread'
    _description = 'Subsidy'

    item_ids = fields.One2many(
        comodel_name='workspace.item',
        inverse_name='subsidy_id',
        string='Items',
    )
    name = fields.Char(
        string='Name',
    )
    description = fields.Char(
        string='Description',
    )
    date = fields.Date(
        string='Date',
    )
    item_count = fields.Integer(
        string="Item Count",
        compute="_compute_item_count",
    )

    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_count)
