# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tests.common import Form
from odoo.exceptions import UserError, ValidationError


class TestHrExpenseAdvanceClearingConsolidation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.ref('base.main_company')
        cls.journal_bank = cls.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        cls.product = cls.env['product.product'].create({
            'name': 'Service 1',
            'type': 'service',
        })
        employee_home = cls.env['res.partner'].create({
            'name': 'Employee Home Address',
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employee A',
            'address_home_id': employee_home.id,
        })
        advance_account = cls.env['account.account'].create({
            'code': '154000',
            'name': 'Employee Advance',
            'user_type_id': cls.env.ref(
                'account.data_account_type_current_assets').id,
            'reconcile': True,
        })
        cls.emp_advance = cls.env.ref('hr_expense_advance_clearing.'
                                      'product_emp_advance')
        cls.emp_advance.property_account_expense_id = advance_account
        # Create advance expense 1,000
        cls.advance1 = cls._create_expense_sheet(
            cls, 'Advance1 1,000', cls.employee, cls.emp_advance, 1000.0,
            advance=True)
        cls.advance2 = cls._create_expense_sheet(
            cls, 'Advance2 1,000', cls.employee, cls.emp_advance, 1000.0,
            advance=True)
        cls.advance3 = cls._create_expense_sheet(
            cls, 'Advance3 1,000', cls.employee, cls.emp_advance, 1000.0,
            advance=True)

        # Create clearing expense 800
        cls.clearing_less = cls._create_expense_sheet(
            cls, 'Buy service 800', cls.employee, cls.product, 800.0)

        # Create clearing expense 800 - not done
        cls.clearing_not_done = cls._create_expense_sheet(
            cls, 'Buy service 800', cls.employee, cls.product, 800.0)

    def _create_expense(self, description, employee,
                        product, amount, advance=False,
                        payment_mode='own_account'):
        with Form(self.env['hr.expense']) as expense:
            expense.advance = advance
            expense.name = description
            expense.employee_id = employee
            expense.product_id = product
            expense.unit_amount = amount
            expense.payment_mode = payment_mode
        expense = expense.save()
        expense.tax_ids = False  # Test no vat
        return expense

    def _create_expense_sheet(self, description, employee,
                              product, amount, advance=False):
        expense = self._create_expense(self, description, employee,
                                       product, amount, advance)
        # Add expense to expense sheet
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': description,
            'employee_id': expense.employee_id.id,
            'expense_line_ids': [(6, 0, [expense.id])],
        })
        return expense_sheet

    def _register_payment(self, expense_sheet, hr_return_advance=False):
        ctx = {'active_ids': [expense_sheet.id],
               'active_id': expense_sheet.id,
               'hr_return_advance': hr_return_advance, }
        PaymentWizard = self.env['hr.expense.sheet.register.payment.wizard']
        with Form(PaymentWizard.with_context(ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wizard = f.save()
        payment_wizard.expense_post_payment()

    def test_0_test_constraints(self):
        """ Test some constraints """
        # Advance Sheet can't be clearing at the same time.
        with self.assertRaises(ValidationError):
            self.advance1.advance_sheet_id = self.advance1

    def test_1_consolidate_open_advances(self):
        """ When clear less than advance, do return advance """

        # ------------------ Advance1 --------------------------
        self.advance1.action_submit_sheet()
        self.advance1.approve_expense_sheets()
        self.advance1.action_sheet_move_create()
        self.assertEqual(self.advance1.clearing_residual, 1000.0)
        self._register_payment(self.advance1)
        self.assertEqual(self.advance1.state, 'done')

        # ------------------ Advance2 --------------------------
        self.advance2.action_submit_sheet()
        self.advance2.approve_expense_sheets()
        self.advance2.action_sheet_move_create()
        self.assertEqual(self.advance2.clearing_residual, 1000.0)
        self._register_payment(self.advance2)
        self.assertEqual(self.advance2.state, 'done')

        # ------------------ Clearing --------------------------
        # Clear this with previous advance
        self.clearing_less.advance_sheet_id = self.advance1
        self.assertEqual(self.clearing_less.advance_sheet_residual, 1000.0)
        self.clearing_less.action_submit_sheet()
        self.clearing_less.approve_expense_sheets()
        self.clearing_less.action_sheet_move_create()
        # Less amount, state set to done. Still remain 200 to be returned
        self.assertEqual(self.clearing_less.state, 'done')
        self.assertEqual(self.clearing_less.advance_sheet_residual, 200.0)

        # Consolidation advance1 and advance2
        advances = self.advance1 + self.advance2
        consolidated_advance = advances._consolidate_open_advances()

        self.assertTrue(consolidated_advance)
        self.assertEqual(consolidated_advance.clearing_residual, 1200.0)
        self.assertEqual(consolidated_advance.state, 'done')

        # Try consolidate only one advance
        with self.assertRaises(UserError):
            consolidated_advance._consolidate_open_advances()

        # Try consolidate advance3 and consolidated_advance
        advances = self.advance3 + consolidated_advance
        with self.assertRaises(UserError):
            advances._consolidate_open_advances()

        # ------------------ Advance3 --------------------------
        self.advance3.action_submit_sheet()
        self.advance3.approve_expense_sheets()
        self.advance3.action_sheet_move_create()
        self.assertEqual(self.advance3.clearing_residual, 1000.0)

        # Try consolidate advance3 not done but with clearing residual value > 0 and
        # consolidated_advance
        with self.assertRaises(UserError):
            advances._consolidate_open_advances()

        self._register_payment(self.advance3)
        self.assertEqual(self.advance3.state, 'done')

        # Try consolidate advance3 clearing_not_done and consolidated_advance
        self.clearing_not_done.advance_sheet_id = self.advance3
        with self.assertRaises(UserError):
            advances._consolidate_open_advances()
