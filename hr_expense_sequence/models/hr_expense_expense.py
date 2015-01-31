# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class HrExpense(models.Model):
    _inherit = 'hr.expense.expense'

    number = fields.Char(required=True, default="/", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].get('hr.expense')
        return super(HrExpense, self).create(vals)
