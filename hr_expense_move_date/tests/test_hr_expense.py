# -*- coding: utf-8 -*-
# Copyright 2016-17 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import time


class ExpenseMoveDateCase(TransactionCase):

    def setUp(self):
        super(ExpenseMoveDateCase, self).setUp()
        self.hr_expense = self.env['hr.expense']
        self.hr_expense_sheet = self.env['hr.expense.sheet']
        self.account_tax = self.env['account.tax']
        self.product = self.env.ref('hr_expense.air_ticket')
        self.employee = self.env.ref('hr.employee_mit')

        self.tax = self.account_tax.create({
            'name': 'Expense 10%',
            'amount': 10,
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'price_include': True,
        })
        self.product.write({
            'supplier_taxes_id': [(6, 0, [self.tax.id])]
        })
        self.expense = self.hr_expense_sheet.create({
            'name': 'Expense for John Smith',
            'employee_id': self.employee.id,
        })
        self.expense_line = self.hr_expense.create({
            'name': 'Car Travel Expenses',
            'employee_id': self.employee.id,
            'product_id': self.product.id,
            'unit_amount': 700.00,
            'date': time.strftime('%Y-%m-%d'),
            'move_date': time.strftime('%Y-%m-10'),
            'tax_ids': [(6, 0, [self.tax.id])],
            'sheet_id': self.expense.id,
        })

    def test_expense_1(self):
        self.expense.approve_expense_sheets()
        self.expense.action_sheet_move_create()
        move = self.expense.account_move_id
        self.assertEqual(self.expense.expense_line_ids.move_date, move.date)
