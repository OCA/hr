# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import TransactionCase


class TestResPartnerBankRestrict(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_employee = cls.env["res.partner"].create(
            {
                "name": "Employee Contact",
                "email": "employee@test.com",
            }
        )
        cls.partner_regular = cls.env["res.partner"].create(
            {
                "name": "Regular Contact",
                "email": "regular@test.com",
            }
        )
        cls.bank = cls.env["res.bank"].create(
            {
                "name": "Test Bank",
                "bic": "TESTBANK",
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "work_contact_id": cls.partner_employee.id,
            }
        )
        cls.bank_account_employee = cls.env["res.partner.bank"].create(
            {
                "partner_id": cls.partner_employee.id,
                "acc_number": "ES123456789012345678",
                "bank_id": cls.bank.id,
            }
        )
        cls.bank_account_regular = cls.env["res.partner.bank"].create(
            {
                "partner_id": cls.partner_regular.id,
                "acc_number": "ES987654321098765432",
                "bank_id": cls.bank.id,
            }
        )
        cls.user_account_manager = new_test_user(
            cls.env,
            name="Batman Accountant",
            email="user_account_manager@test.com",
            groups="base.group_user,account.group_account_manager",
            login="user_account_manager",
        )
        cls.user_account_user = new_test_user(
            cls.env,
            name="Robin Accountant",
            email="user_account_user@test.com",
            groups="base.group_user,account.group_account_user",
            login="user_account_user",
        )
        cls.user_account_invoice = new_test_user(
            cls.env,
            name="Batgirl Accountant",
            email="user_account_invoice@test.com",
            groups="base.group_user,account.group_account_invoice",
            login="user_account_invoice",
        )
        cls.user_no_account = new_test_user(
            cls.env,
            name="Alfred Accountant",
            email="user_no_account@test.com",
            groups="base.group_user",
            login="user_no_account",
        )
        cls.all_users = (
            cls.user_account_manager
            | cls.user_account_user
            | cls.user_account_invoice
            | cls.user_no_account
        )
        cls.not_restrict_users = cls.user_account_manager | cls.user_account_user
        cls.restrict_users = cls.user_account_invoice | cls.user_no_account

    def test_partner_employee_contact_is_detected(self):
        """Test a partner related to an employee is detected as employee contact."""
        self.assertTrue(self.partner_employee._is_employee_contact())

    def test_partner_regular_contact_is_not_employee(self):
        """Test a regular partner is not detected as employee contact."""
        self.assertFalse(self.partner_regular._is_employee_contact())

    def test_partner_regular_can_view_bank_accounts(self):
        """Test regular partners show bank accounts to all users."""
        for user in self.all_users:
            with self.subTest(user=user):
                self.assertTrue(
                    self.partner_regular.with_user(user)._check_can_view_bank_accounts()
                )

    def test_partner_with_employee_can_view_bank_accounts_regular_contact(self):
        """Test employee partners show bank accounts only to accounting users."""
        for user in self.not_restrict_users:
            with self.subTest(user=user):
                self.assertTrue(
                    self.partner_employee.with_user(
                        user
                    )._check_can_view_bank_accounts()
                )
        for user in self.restrict_users:
            with self.subTest(user=user):
                self.assertFalse(
                    self.partner_employee.with_user(
                        user
                    )._check_can_view_bank_accounts()
                )
