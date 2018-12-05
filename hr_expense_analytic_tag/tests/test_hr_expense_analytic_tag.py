# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestHrExpenseAnalyticTag(common.TransactionCase):

    def setUp(self):
        super(TestHrExpenseAnalyticTag, self).setUp()

        analytic_tag_obj = self.env['account.analytic.tag']
        self.tag1 = analytic_tag_obj.create({'name': 'Tag1'})
        self.tag2 = analytic_tag_obj.create({'name': 'Tag2'})

        self.expense = self.env['hr.expense'].create({
            'name': 'Expense test',
            'product_id': self.ref('hr_expense.hotel_rent'),
            'unit_amount': 1,
            'quantity': 10,
            'analytic_account_id': self.ref(
                'analytic.analytic_our_super_product'),
            'analytic_tag_ids': [[6, 0, (self.tag1 | self.tag2).ids]],
        })
        self.expense._onchange_product_id()

    def test_prepare_move_line(self):
        move_lines = self.expense._move_line_get()[0]
        move_lines.update(
            date_maturity=self.expense.date,
            amount_currency=False,
        )
        move_line_vals = self.expense._prepare_move_line(move_lines)
        tag_ids = move_line_vals['analytic_tag_ids']
        self.assertEqual(tag_ids, [[4, self.tag1.id], [4, self.tag2.id]])

    def test_action_sheet_move_create(self):
        sheet = self.env['hr.expense.sheet'].create({
            'employee_id': self.expense.employee_id.id,
            'name': self.expense.name,
        })
        self.expense.sheet_id = sheet.id
        sheet.approve_expense_sheets()
        sheet.action_sheet_move_create()

        lines = sheet.account_move_id.line_ids.mapped('analytic_line_ids')
        tags = lines.mapped('tag_ids')
        self.assertEqual(tags, self.tag1 | self.tag2)
