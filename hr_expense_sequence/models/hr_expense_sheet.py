# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    _rec_name = 'number'

    number = fields.Char(required=True, default='/', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            number = self.env['ir.sequence'].next_by_code('hr.expense.sheet')
            vals['number'] = number
        return super(HrExpenseSheet, self).create(vals)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        names1 = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Make the other search
        names2 = []
        if name:
            domain = [("number", "=ilike", name + "%")]
            names2 = self.search(domain, limit=limit).name_get()
        # Merge both results
        return list(set(names1) | set(names2))[:limit]
