# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import openerp.tests.common as common


class TestCommission(common.TransactionCase):

    def setUp(self):
        super(TestCommission, self).setUp()

        self.main_company = self.env.ref('base.main_company')
        self.main_company.currency_id = self.env.ref("base.CHF").id
        self.sale_user = self.env['res.users'].with_context(
            {'no_reset_password': True}
        ).create(
            {
                'name': "Salesman",
                'company_id': self.main_company.id,
                'login': "sale",
                'email': "sale@yourcompany.com",
            }
        )

        self.employee = self.env['hr.employee'].create(
            {
                'name': 'TEST',
                'user_id': self.sale_user.id
            }
        )
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_4")

        self.account_receivable = self.env['account.account'].search(
            [(
                'user_type_id', '=',
                self.env.ref('account.data_account_type_receivable').id
            )],
            limit=1
        )

        self.account_revenue = self.env['account.account'].search(
            [(
                'user_type_id', '=',
                self.env.ref('account.data_account_type_revenue').id
            )],
            limit=1
        )

    def test_comission(self):
        self.invoice = self.env['account.invoice'].create(
            {
                'name': 'Invoice',
                'user_id': self.sale_user.id,
                'reference_type': 'none',
                'account_id': self.account_receivable.id,
                'partner_id': self.partner.id,
                'type': 'out_invoice',
                'currency_id': self.env.ref("base.CHF").id,
                'date_invoice': datetime.datetime.today()
            }
        )
        self.invoice_line = self.env['account.invoice.line'].create(
            {
                'product_id': self.product.id,
                'price_unit': 500,
                'quantity': 1,
                'invoice_id': self.invoice.id,
                'account_id': self.account_revenue.id,
                'name': "Invoice Line"
            }
        )
        self.invoice.signal_workflow('invoice_open')
        self.bank_journal = self.env['account.journal'].create(
            {
                'name': 'Bank',
                'type': 'bank',
                'code': 'BNK',
            }
        )
        ctx = {
            'active_model': 'account.invoice', 'active_ids': [self.invoice.id]
        }
        reg_payment_obj = self.env['account.register.payments']
        self.payment_method_id = self.env.ref(
            "account.account_payment_method_manual_in").id
        self.register_payments = reg_payment_obj.with_context(ctx).create(
            {
                'journal_id': self.bank_journal.id,
                'payment_method_id': self.payment_method_id,
                'amount': 500,
                'payment_date': datetime.datetime.today(),
                'payment_type': 'inbound',
            }
        )
        self.contract = self.env['hr.contract'].create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract',
                'wage': 0,
                'comm_rate': 0.2,
            }
        )
        self.register_payments.create_payment()
        self.assertEqual(self.employee.contract_id.commission, 500)

        self.commission_rule = self.env['hr.salary.rule'].search(
            [
                ['code', '=', 'COMM']
            ]
        )
        if self.commission_rule:
            self.payroll_structure = self.env['hr.payroll.structure'].create(
                {
                    'name': 'Test structure',
                    'code': "TEST",
                    'rule_ids': [(4, self.commission_rule.id)],
                    'parent_id': False,
                }
            )
            self.contract.struct_id = self.payroll_structure.id
            self.payslip = self.env['hr.payslip'].create(
                {
                    'employee_id': self.employee.id,
                    'contract_id': self.contract.id,
                    'struct_id': self.payroll_structure.id,
                }
            )
            self.payslip.compute_sheet()
            self.assertEqual(self.payslip.line_ids[0].amount, 100)
