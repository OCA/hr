# -*- coding: utf-8 -*-
#
#  File: models/hr_payslip.py
#  Module: hr_payroll_expense
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2015-TODAY Open-Net Ltd.
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


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    expenses = fields.One2many('hr.expense', 'slip_id',
                               string='Expenses')

    @api.multi
    def compute_sheet(self):
        # Detach expenses from the pay slips
        ExpenseObj = self.env['hr.expense']
        expenses = ExpenseObj.search([('slip_id', 'in', self.ids)])
        if expenses:
            expenses.write({'slip_id': False})

        res = super(HrPayslip, self).compute_sheet()

        # Then, re-link the expenses

        for payslip in self:
            employee_id = payslip.contract_id.employee_id.id

            # Look for expenses
            filters = [
                ('employee_id', '=', employee_id),
                ('slip_id', '=', False),
                ('state', '=', ['done', 'post']),
            ]
            expenses = ExpenseObj.search(filters)
            if expenses:
                expenses.write({'slip_id': payslip.id})

        return res

    def process_sheet(self):
        ExpenseObj = self.env['hr.expense']
        expenses = ExpenseObj.search([
            ('slip_id', '=', self.id)
        ])
        for expense in expenses:
            expenses.state = 'done'
        return super(HrPayslip, self).process_sheet()