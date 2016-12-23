# -*- coding: utf-8 -*-
# Copyright 2011,2013 Michael Telahun Makonnen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    name = fields.Char('Contract Reference', required=False,
                       readonly=True, copy=False, default='/')

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.ref')
        return super(hr_contract, self).create(vals)
