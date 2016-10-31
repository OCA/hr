# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class PayslipToPaymentCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(PayslipToPaymentCase, self).setUp(*args, **kwargs)

        self.obj_payslip = self.env[
            "hr.payslip"]
        self.obj_payslip_2_payment = self.env[
            "hr.payslip_to_payment_order"]
        self.obj_wizard = self.env[
            "hr.create_payment_order_from_payslip"]
        self.partner1 = self.env[
            "res.partner"].create(
                    {"name": "X Partner 1"})
        self.partner2 = self.env[
            "res.partner"].create(
                    {"name": "X Partner 2"})
        self.partner_bank1 = self.env[
            "res.partner.bank"].create({
                "name": "X Bank1",
                "acc_number": "1234567890",
                "bank": self.env.ref("base.res_bank_1").id,
                "partner_id": self.partner1.id,
                "state": self.env[
                    "res.partner.bank.type"].search([], limit=1).code,
                })
        self.employee1 = self.env.ref(
            "hr.employee_al")
        self.employee2 = self.env.ref(
            "hr.employee_mit")
        self.employee1.write({
            "bank_account_id": self.partner_bank1.id,
            "address_home_id": self.partner1.id,
            })
        self.employee2.write({
            "address_home_id": self.partner2.id,
            })
        self.struct = self.env.ref(
            "hr_payroll.structure_base")
        self.rule1 = self.env.ref(
            "hr_payroll.hr_rule_net")
        self.rule1.write({
            "account_debit": self.env.ref(
                "account.a_salary_expense").id,
            "account_credit": self.env.ref(
                "account.a_pay").id,
            })
        self.contract1 = self.env["hr.contract"].create({
            "name": "X Contract 1",
            "employee_id": self.employee1.id,
            "wage": 7000.00,
            "struct_id": self.struct.id,
            "date_start": self.env.ref(
                "account.data_fiscalyear").date_start,
            })
        self.contract2 = self.env["hr.contract"].create({
            "name": "X Contract 2",
            "employee_id": self.employee2.id,
            "wage": 8000.00,
            "struct_id": self.struct.id,
            "date_start": self.env.ref(
                "account.data_fiscalyear").date_start,
            })
        self.period1 = self.env.ref(
            "account.period_7")
        self.period2 = self.env.ref(
            "account.period_8")

    def _prepare_payslip(
            self, employee, period, contract):
        res = {
            "employee_id": employee.id,
            "date_from": period.date_start,
            "date_to": period.date_stop,
            "contract_id": contract.id,
            "struct_id": contract.struct_id.id,
            }
        return res

    def test_1(self):
        payslip1 = self.obj_payslip.create(
                self._prepare_payslip(
                    self.employee1, self.period1, self.contract1))
        payslip2 = self.obj_payslip.create(
                self._prepare_payslip(
                    self.employee1, self.period2, self.contract1))
        payslip3 = self.obj_payslip.create(
                self._prepare_payslip(
                    self.employee2, self.period1, self.contract2))
        payslip4 = self.obj_payslip.create(
                self._prepare_payslip(
                    self.employee2, self.period2, self.contract2))
        payslips = payslip1 + payslip2 + payslip3 + payslip4
        payslips.signal_workflow("hr_verify_sheet")
        p2ps = self.obj_payslip_2_payment.search([])
        self.assertEqual(
            len(p2ps),
            4)
        for p2p in p2ps:
            if p2p.employee_id.id == self.employee1.id:
                self.assertEqual(
                    p2p.amount,
                    7000.00)
            elif p2p.employee_id.id == self.employee2.id:
                self.assertEqual(
                    p2p.amount,
                    8000.00)
            self.assertEqual(
                p2p.payment_on_progress,
                0)
            self.assertEqual(
                p2p.amount_payment_on_progress,
                0)

        wizard = self.obj_wizard.with_context(
                active_ids=[p2ps[0].id, p2ps[2].id]).create({
                    "bank_cash": "bank",
                    "bank_id": self.env.ref(
                        "base.res_bank_1").id,
                    "mode_id": self.env.ref(
                        "account_payment.payment_mode_1").id,
                    })
        wizard.action_create()
        self.assertEqual(
            p2ps[0].payment_on_progress,
            1)
        self.assertEqual(
            p2ps[0].amount_payment_on_progress,
            7000.00)
        self.assertEqual(
            p2ps[1].payment_on_progress,
            1)
        self.assertEqual(
            p2ps[1].amount_payment_on_progress,
            8000.00)
