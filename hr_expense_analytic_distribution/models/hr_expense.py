# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>.
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution', oldname='analytics_id',
        states={'post': [('readonly', True)], 'done': [('readonly', True)]},
    )

    @api.model
    def _prepare_move_line(self, line):
        result = super(HrExpense, self)._prepare_move_line(line)
        result['analytic_distribution_id'] = self.analytic_distribution_id.id
        return result
