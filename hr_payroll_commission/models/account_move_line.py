# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    slip_id = fields.Many2one('hr.payslip', string='Payslip')
