# -*- coding: utf-8 -*-
#
#  File: models/hr_contract.py
#  Module: hr_payroll_expense
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


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # ---------- Fields management

    @api.one
    @api.depends('employee_id.user_id')
    def _comp_reimbursement(self):
        self.reimbursement = 0

        # Look in linked expenses:
        filters = [
            ('employee_id', '=', self.employee_id.id),
            ('slip_id', '=', False),
            ('state', 'in', ['done', 'post']),
        ]

        # Compute reimbursement
        reimbursement = 0
        ExpensesObj = self.env['hr.expense']
        for expense in ExpensesObj.search(filters):
            reimbursement += expense.account_move_id.amount
        self.reimbursement += reimbursement

    reimbursement = fields.Float(string='Reimbursement',
                                 compute='_comp_reimbursement')
