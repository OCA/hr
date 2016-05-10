# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class ExpenseMoveDateCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(ExpenseMoveDateCase, self).setUp(*args, **kwargs)

        self.expense_demo = self.env.ref('hr_expense.sep_expenses')
        self.expense = self.expense_demo.copy()
        self.period = self.env.ref('account.period_8')

        return result

    def test_expense_1(self):
        self.expense.signal_workflow('confirm')
        self.expense.signal_workflow('validate')

        self.expense.move_date = self.period.date_stop
        self.expense.onchange_move_date()
        self.assertEqual(self.expense.period_id.id, self.period.id)
        self.expense.write({
            'move_date': self.period.date_stop,
            'period_id': self.expense.period_id.id,
        })
        self.assertEqual(self.expense.move_date, self.period.date_stop)
        self.expense.signal_workflow('done')
        self.assertIsNotNone(self.expense.account_move_id)
        move = self.expense.account_move_id
        self.assertEqual(move.date, self.expense.move_date)
