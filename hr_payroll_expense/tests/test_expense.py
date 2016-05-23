# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common


class TestExpense(common.TransactionCase):

    def setUp(self):
        super(TestExpense, self).setUp()

        self.employee = self.env['hr.employee'].create(
            {
                'name': 'TEST',
            }
        )
        self.product = self.env.ref("product.product_product_4")

    def test_expense(self):
        self.expense_rule = self.env['hr.salary.rule'].search(
            [
                ['code', '=', 'REIMB']
            ]
        )
        if self.expense_rule:
            self.payroll_structure = self.env['hr.payroll.structure'].create(
                {
                    'name': 'Test structure',
                    'code': "TEST",
                    'rule_ids': [(4, self.expense_rule.id)],
                    'parent_id': False,
                }
            )
            self.contract = self.env['hr.contract'].create(
                {
                    'employee_id': self.employee.id,
                    'name': 'Contract',
                    'wage': 0,
                    'struct_id': self.payroll_structure.id,
                }
            )
            self.expense = self.env['hr.expense'].create(
                {
                    'employee_id': self.employee.id,
                    'name': 'Expense',
                    'product_id': self.product.id,
                    'unit_amount': 500,
                    'state': 'approve',
                }
            )
            self.assertEqual(self.employee.contract_id.reimbursement, 500)

            self.payslip = self.env['hr.payslip'].create(
                {
                    'employee_id': self.employee.id,
                    'contract_id': self.contract.id,
                }
            )
            self.payslip.compute_sheet()
            self.assertEqual(self.payslip.line_ids[0].amount, 500)
