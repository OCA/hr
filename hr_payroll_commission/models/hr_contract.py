# -*- coding: utf-8 -*-
#
#  File: models/hr_contract.py
#  Module: hr_payroll_commission
#
#  Created by sge@open-net.ch
#
#  Copyright (c) 2015 Open-Net Ltd.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # ---------- Fields management

    @api.one
    @api.depends('employee_id.user_id')
    def _comp_commission(self):
        self.commission = 0

        account_invoice_obj = self.env['account.invoice']
        invoice_ids = account_invoice_obj.search([
            ('state', 'in', ('open', 'paid')),
            ('user_id', '=', self.employee_id.user_id.id),
            ('type', '=', 'out_invoice'),
            ('slip_id', '=', False)
        ])

        # Compute comission based
        commission = 0
        for invoice_id in invoice_ids:
            for move_line in invoice_id.payment_move_line_ids:
                if not move_line.slip_id.id:
                    commission += move_line.credit
        self.commission += commission

    commission = fields.Float(string='Commission',
                              compute='_comp_commission')
    comm_rate = fields.Float(string='Commissions Rate',
                             digits=dp.get_precision('Payroll Rate'))
