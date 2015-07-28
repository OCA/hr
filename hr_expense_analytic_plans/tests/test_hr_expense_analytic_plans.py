# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
from openerp.tests.common import TransactionCase


class TestHrExpenseAnalyticPlans(TransactionCase):
    def test_hr_expense_analytic_plans(self):
        account1 = self.env['account.analytic.account'].create({
            'name': 'account1',
        })
        account2 = self.env['account.analytic.account'].create({
            'name': 'account2',
        })
        instance = self.env['account.analytic.plan.instance'].create({
            'name': 'plan',
            'account_ids': [
                (0, 0, {
                    'rate': 50,
                    'analytic_account_id': account1.id,
                }),
                (0, 0, {
                    'rate': 50,
                    'analytic_account_id': account2.id,
                }),
            ],
        })
        expense = self.env['hr.expense.expense'].create({
            'employee_id': self.env.ref('hr.employee_mit').id,
            'name': 'testexpense',
            'line_ids': [
                (0, 0, {
                    'name': 'testline',
                    'analytics_id': instance.id,
                    'unit_amount': 42,
                    'unit_quantity': 1,
                }),
            ],
        })
        expense.signal_workflow('confirm')
        expense.signal_workflow('validate')
        expense.signal_workflow('done')
        for line in expense.account_move_id.line_id:
            if line.analytic_lines:
                self.assertEqual(len(line.analytic_lines), 2)
                self.assertIn(account1, [
                    l.account_id for l in line.analytic_lines])
                self.assertIn(account2, [
                    l.account_id for l in line.analytic_lines])
                for l in line.analytic_lines:
                    self.assertEqual(l.amount, -21)
