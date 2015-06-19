# -*- coding: utf-8 -*-
#
##############################################################################
#
#     Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.tests import common
from openerp import workflow


def create_basic_expense(self, employee):
    data = {'employee_id': employee.id,
            'name': 'Test',
            'line_ids': [(0, 0, {'name': 'Test',
                                 'unit_amount': 100})]
            }
    expense = self.expense_obj.create(data)
    return expense


class TestHrExpenseAccountPeriod(common.TransactionCase):

    def setUp(self):
        super(TestHrExpenseAccountPeriod, self).setUp()
        self.expense_obj = self.env['hr.expense.expense']
        self.period01 = self.env.ref('account.period_1')
        self.period02 = self.env.ref('account.period_2')

    def common_test(self):
        employee = self.env.ref('hr.employee')
        partner = self.env.ref('base.partner_root')
        # I set a partner as home address for employee
        employee.address_home_id = partner
        # I create an expense
        self.expense = create_basic_expense(self, employee)
        # I click on Submit to manager button
        workflow.trg_validate(self.uid, 'hr.expense.expense', self.expense.id,
                              'confirm', self.cr)
        # For the test, I change date_confirm
        self.expense.date_confirm = self.period01.date_stop
        # I check if the state is confirm
        self.assertEqual(self.expense.state, 'confirm',
                         "Expense's state isn't confirm")
        # I click on Approve
        workflow.trg_validate(self.uid, 'hr.expense.expense', self.expense.id,
                              'validate', self.cr)
        # I check if the state is Approved
        self.assertEqual(self.expense.state, 'accepted',
                         "Expense's state isn't approved")

    def test_hr_expense_account_period(self):
        self.common_test()
        # I click on Generate Accounting Entries
        workflow.trg_validate(self.uid, 'hr.expense.expense', self.expense.id,
                              'done', self.cr)
        # I check if the state is Done
        self.assertEqual(self.expense.state, 'done',
                         "Expense's state isn't done")
        # I check if the used period is period01
        self.assertEqual(self.expense.account_move_id.period_id.id,
                         self.period01.id, "Period isn't correct")

    def test_hr_expense_account_force_period(self):
        self.common_test()
        # I force the period
        self.expense.period_id = self.period02
        # I click on Generate Accounting Entries
        workflow.trg_validate(self.uid, 'hr.expense.expense', self.expense.id,
                              'done', self.cr)
        # I check if the state is Done
        self.assertEqual(self.expense.state, 'done',
                         "Expense's state isn't done")
        # I check if the used period is the period defined on the expense
        self.assertEqual(self.expense.account_move_id.period_id.id,
                         self.period02.id, "Period isn't correct")
