# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tests.common import Form


class TestHrExpenseAdvanceClearing(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrExpenseAdvanceClearing, cls).setUpClass()
        company = cls.env.ref("base.main_company")
        cls.journal_bank = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Service 1", "type": "service"}
        )
        tax_group = cls.env["account.tax.group"].create(
            {"name": "Tax Group 1", "sequence": 1}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 10.0%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "company_id": company.id,
                "tax_group_id": tax_group.id,
            }
        )
        employee_home = cls.env["res.partner"].create({"name": "Employee Home Address"})
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Employee A", "address_home_id": employee_home.id}
        )
        advance_account = cls.env["account.account"].create(
            {
                "code": "154000",
                "name": "Employee Advance",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
                "reconcile": True,
            }
        )
        cls.emp_advance = cls.env.ref(
            "hr_expense_advance_clearing." "product_emp_advance"
        )
        cls.emp_advance.property_account_expense_id = advance_account
        # Create advance expense 1,000
        cls.advance = cls._create_expense_sheet(
            cls, "Advance 1,000", cls.employee, cls.emp_advance, 1000.0, advance=True
        )
        # Create clearing expense 1,000
        cls.clearing_equal = cls._create_expense_sheet(
            cls, "Buy service 1,000", cls.employee, cls.product, 1000.0
        )
        # Create clearing expense 1,200
        cls.clearing_more = cls._create_expense_sheet(
            cls, "Buy service 1,200", cls.employee, cls.product, 1200.0
        )
        # Create clearing expense 800
        cls.clearing_less = cls._create_expense_sheet(
            cls, "Buy service 800", cls.employee, cls.product, 800.0
        )

    def _create_expense(
        self,
        description,
        employee,
        product,
        amount,
        advance=False,
        payment_mode="own_account",
    ):
        with Form(self.env["hr.expense"]) as expense:
            expense.advance = advance
            expense.name = description
            expense.employee_id = employee
            expense.product_id = product
            expense.unit_amount = amount
            expense.payment_mode = payment_mode
        expense = expense.save()
        expense.tax_ids = False  # Test no vat
        return expense

    def _create_expense_sheet(
        self, description, employee, product, amount, advance=False
    ):
        expense = self._create_expense(
            self, description, employee, product, amount, advance
        )
        # Add expense to expense sheet
        expense_sheet = self.env["hr.expense.sheet"].create(
            {
                "name": description,
                "employee_id": expense.employee_id.id,
                "expense_line_ids": [(6, 0, [expense.id])],
            }
        )
        return expense_sheet

    def _register_payment(self, expense_sheet, hr_return_advance=False):
        ctx = {
            "active_ids": [expense_sheet.id],
            "active_id": expense_sheet.id,
            "hr_return_advance": hr_return_advance,
            "active_model": "hr.expense.sheet",
        }
        PaymentWizard = self.env["hr.expense.sheet.register.payment.wizard"]
        with Form(PaymentWizard.with_context(ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wizard = f.save()
        payment_wizard.expense_post_payment()

    def test_0_test_constraints(self):
        """ Test some constraints """
        # Advance Sheet can't be clearing at the same time.
        with self.assertRaises(ValidationError):
            self.advance.advance_sheet_id = self.advance
        # Advance Sheet should not have > 1 expense lines
        with self.assertRaises(ValidationError):
            expense = self._create_expense(
                "Buy service 1,000", self.employee, self.product, 1.0
            )
            self.advance.write({"expense_line_ids": [(4, expense.id)]})
        # Advance Expense's product must be employee advance
        with self.assertRaises(ValidationError):
            expense = self._create_expense(
                "Advance 1,000", self.employee, self.product, 1.0, advance=True
            )
        # Advance Expense's product, must not has tax involved
        with self.assertRaises(ValidationError):
            self.emp_advance.supplier_taxes_id |= self.tax
            expense = self._create_expense(
                "Advance 1,000", self.employee, self.emp_advance, 1.0, advance=True
            )
        self.emp_advance.supplier_taxes_id = False  # Remove tax bf proceed
        # Advance Expense, must not paid by company
        with self.assertRaises(ValidationError):
            expense = self._create_expense(
                "Advance 1,000",
                self.employee,
                self.emp_advance,
                1.0,
                advance=True,
                payment_mode="company_account",
            )
        # Advance Expense's product must have account configured
        with self.assertRaises(ValidationError):
            self.emp_advance.property_account_expense_id = False
            expense = self._create_expense(
                "Advance 1,000", self.employee, self.emp_advance, 1.0, advance=True
            )

    def test_1_clear_equal_advance(self):
        """ When clear equal advance, all set """
        # ------------------ Advance --------------------------
        self.advance.action_submit_sheet()
        self.advance.approve_expense_sheets()
        self.advance.action_sheet_move_create()
        self.assertEqual(self.advance.residual, 1000.0)
        self._register_payment(self.advance)
        self.assertEqual(self.advance.state, "done")
        # ------------------ Clearing --------------------------
        # Clear this with previous advance
        vals = self.advance.open_clear_advance()  # Test Clear Advance button
        ctx = vals.get("context")
        self.assertEqual(ctx["default_advance_sheet_id"], self.advance.id)
        self.clearing_equal.advance_sheet_id = self.advance
        self.assertEqual(self.clearing_equal.advance_sheet_residual, 1000.0)
        self.clearing_equal.action_submit_sheet()
        self.clearing_equal.approve_expense_sheets()
        self.clearing_equal.action_sheet_move_create()
        # Equal amount, state change to Paid and advance is cleared
        self.assertEqual(self.clearing_equal.state, "done")
        self.assertEqual(self.clearing_equal.advance_sheet_residual, 0.0)

    def test_2_clear_more_than_advance(self):
        """ When clear more than advance, do pay more """
        # ------------------ Advance --------------------------
        self.advance.action_submit_sheet()
        self.advance.approve_expense_sheets()
        self.advance.action_sheet_move_create()
        self.assertEqual(self.advance.residual, 1000.0)
        self._register_payment(self.advance)
        self.assertEqual(self.advance.state, "done")
        # ------------------ Clearing --------------------------
        # Clear this with previous advance
        self.clearing_more.advance_sheet_id = self.advance
        self.assertEqual(self.clearing_more.advance_sheet_residual, 1000.0)
        self.clearing_more.action_submit_sheet()
        self.clearing_more.approve_expense_sheets()
        self.clearing_more.action_sheet_move_create()
        # More amount, state not changed to paid, and has to pay 200 more
        self.assertEqual(self.clearing_more.state, "post")
        self.assertEqual(self.clearing_more.amount_payable, 200.0)
        self._register_payment(self.clearing_more)
        self.assertEqual(self.clearing_more.state, "done")

    def test_3_clear_less_than_advance(self):
        """ When clear less than advance, do return advance """
        # ------------------ Advance --------------------------
        self.advance.action_submit_sheet()
        self.advance.approve_expense_sheets()
        self.advance.action_sheet_move_create()
        self.assertEqual(self.advance.residual, 1000.0)
        self._register_payment(self.advance)
        self.assertEqual(self.advance.state, "done")
        # ------------------ Clearing --------------------------
        # Clear this with previous advance
        self.clearing_less.advance_sheet_id = self.advance
        self.assertEqual(self.clearing_less.advance_sheet_residual, 1000.0)
        self.clearing_less.action_submit_sheet()
        self.clearing_less.approve_expense_sheets()
        self.clearing_less.action_sheet_move_create()
        # Less amount, state set to done. Still remain 200 to be returned
        self.assertEqual(self.clearing_less.state, "done")
        self.assertEqual(self.clearing_less.advance_sheet_residual, 200.0)
        # Back to advance and do return advance, residual become 0.0
        self._register_payment(self.advance, hr_return_advance=True)
        self.assertEqual(self.advance.residual, 0.0)
