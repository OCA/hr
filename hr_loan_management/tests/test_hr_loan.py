# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp import models
from openerp.exceptions import Warning as UserError


class TestEmployeeLoan(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestEmployeeLoan, self).setUp(*args, **kwargs)

        self.employee = self.env.ref("hr.employee")
        self.partner = self.env.ref("base.partner_root")
        self.employee.write({
            "address_home_id": self.partner.id})
        self.journal = self.env.ref("account.bank_journal")
        self.bank_acc = self.journal.default_debit_account_id
        self.year = self.env.ref("account.data_fiscalyear")

        self.obj_loan = self.env["hr.loan"]
        self.obj_move = self.env["account.move"]
        self.obj_line = self.env["account.move.line"]
        self.obj_period = self.env["account.period"]
        self.obj_realize = self.env[
            "hr.loan.realize_interest"]

    def _realized_loan(self, loan):
        move = self.obj_move.create({
            "name": "X Realization",
            "date": loan.date_realization,
            "journal_id": self.journal.id,
            "period_id": self.obj_period.find(loan.date_realization)[0].id,
        })
        self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": self.bank_acc.id,
            "credit": loan.total_principle_amount,
            "debit": 0.0,
        })
        line = self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": loan.move_line_header_id.account_id.id,
            "debit": loan.total_principle_amount,
            "credit": 0.0,
        })
        (line + loan.move_line_header_id).reconcile_partial()

    def _pay_principle(self, schedule):
        move = self.obj_move.create({
            "name": "X Realization",
            "date": schedule.schedule_date,
            "journal_id": self.journal.id,
            "period_id": self.obj_period.find(schedule.schedule_date)[0].id,
        })
        self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": self.bank_acc.id,
            "debit": schedule.principle_amount,
            "credit": 0.0,
        })
        line = self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": schedule.principle_move_line_id.account_id.id,
            "debit": 0.0,
            "credit": schedule.principle_amount,
        })
        (line + schedule.principle_move_line_id).reconcile_partial()

    def _pay_interest(self, schedule):
        move = self.obj_move.create({
            "name": "X Realization",
            "date": schedule.schedule_date,
            "journal_id": self.journal.id,
            "period_id": self.obj_period.find(schedule.schedule_date)[0].id,
        })
        self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": self.bank_acc.id,
            "debit": schedule.interest_amount,
            "credit": 0.0,
        })
        line = self.obj_line.create({
            "name": "X",
            "move_id": move.id,
            "account_id": schedule.interest_move_line_id.account_id.id,
            "debit": 0.0,
            "credit": schedule.interest_amount,
        })
        (line + schedule.interest_move_line_id).reconcile_partial()

    def _realize_interest(self, schedule):
        wizard = self.obj_realize.with_context(
            active_ids=[schedule.id]).create({})
        wizard.action_realize()

    def _prepare_loan(self,
                      loan_type_id, manual_loan_period=10,
                      loan_amount=2000.00,
                      first_payment_date=False,
                      employee=False,
                      date_payment=7):
        if not first_payment_date:
            first_payment_date = self.year.date_start

        if not employee:
            employee = self.obj_loan._default_employee_id()

        return {
            "employee_id": employee.id,
            "request_date": self.year.date_start,
            "loan_type_id": loan_type_id,
            "loan_amount": loan_amount,
            "manual_loan_period": manual_loan_period,
            "first_payment_date": first_payment_date,
            "date_payment": date_payment,
            "date_realization": self.year.date_start,
            "interest": 10.0,
        }

    def _workflow_confirm(self, loan):
        loan.workflow_action_confirm()
        self.assertEqual(
            loan.state,
            "confirm")

    def _workflow_approve(
            self, loan):
        loan.workflow_action_approve()
        self.assertEqual(
            loan.state,
            "approve")
        self.assertTrue(
            loan.move_receivable_id)
        self.assertEqual(
            loan.move_line_header_id.partner_id,
            loan.employee_id.address_home_id)

    def _workflow_draft(
            self, loan):
        loan.workflow_action_draft()
        self.assertEqual(
            loan.state,
            "draft")

    def _workflow_manual_active(self, loan):
        obj_wizard = self.env["hr.manual_realization"]
        wizard = obj_wizard.with_context(active_id=loan.id).create({
            "realization_date": datetime.today().strftime(
                "%Y-%m-%d"),
        })
        wizard.action_apply()
        self.assertEqual(
            loan.state,
            "active")
        self.assertEqual(
            loan.manual_realization,
            True)

    def _workflow_active(self, loan):
        statement = self.obj_statement.create({
            "date": datetime.today().strftime("%Y-%m-%d"),
            "journal_id": self.journal.id,
        })
        wizard = self.obj_import.with_context(
            active_id=statement.id).create({
                "employee_loan_ids": [(6, 0, [loan.id])],
            })
        wizard.action_import()
        self.assertTrue(loan.statement_line_id)
        self.assertEqual(
            loan.state,
            "active")
        self.assertEqual(
            loan.manual_realization,
            False)

    def _workflow_done(self, loan):
        loan.workflow_action_done()
        self.assertEqual(
            loan.state,
            "done")

    def _workflow_cancel(self, loan):
        loan.workflow_action_cancel()
        self.assertEqual(
            loan.state,
            "cancel")

    def _workflow_cancel_not_allowed(self, loan):
        with self.assertRaises(models.ValidationError):
            loan.workflow_action_cancel()

    def _unlink_allowed(self, loan):
        loan.unlink()

    def _force_unlink(self, loan):
        loan.with_context(force_unlink=True).unlink()

    def _unlink_not_allowed(self, loan):
        with self.assertRaises(UserError):
            loan.unlink()

    def test_no_loan_period_zero(self):
        """
        Loan period can not equal 0
        """
        with self.assertRaises(models.ValidationError):
            self.env["hr.loan"].create(
                self._prepare_loan(
                    self.env.ref("hr_loan_management.loan_type_02").id,
                    0,
                ))

    def test_exceed_max_period(self):
        """
        Loan period can not exceed max. loan period
        """
        with self.assertRaises(models.ValidationError):
            self.env["hr.loan"].create(
                self._prepare_loan(
                    self.env.ref("hr_loan_management.loan_type_01").id,
                    13,
                ))

    def test_exceed_loan_max(self):
        """
        Loan amount can not exceed max. loan amount
        """
        with self.assertRaises(models.ValidationError):
            self.env["hr.loan"].create(
                self._prepare_loan(
                    self.env.ref("hr_loan_management.loan_type_01").id,
                    12,
                    7000.00
                ))

    def test_no_negative_loan_amount(self):
        """
        Loan amount can not less than 0
        """
        with self.assertRaises(models.ValidationError):
            self.env["hr.loan"].create(
                self._prepare_loan(
                    self.env.ref("hr_loan_management.loan_type_01").id,
                    12,
                    -1000.00
                ))

    def test_cancel_on_draft(self):
        """
        Cancel on draft state
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_01").id,
                1,
                1200.00,
            ))
        loan.action_compute_payment()
        self._workflow_cancel(loan)
        self._unlink_allowed(loan)

    def test_cancel_on_confirm(self):
        """
        Cancel on confirm state
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_01").id,
                1,
                1200.00,
            ))
        loan.action_compute_payment()
        self._workflow_confirm(loan)
        self._workflow_cancel(loan)
        self._unlink_not_allowed(loan)
        self._force_unlink(loan)

    def test_cancel_on_approve(self):
        """
        Cancel on confirm state
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_01").id,
                1,
                1200.00,
            ))
        loan.action_compute_payment()
        self._workflow_confirm(loan)
        self._workflow_approve(loan)
        self._workflow_cancel(loan)
        self._unlink_not_allowed(loan)
        self._force_unlink(loan)

    def test_cancel_on_active(self):
        """
        Cancel on confirm active
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_01").id,
                1,
                1200.00,
            ))
        loan.action_compute_payment()
        self._workflow_confirm(loan)
        self._workflow_approve(loan)
        self._realized_loan(loan)
        self._workflow_cancel_not_allowed(loan)
        self._unlink_not_allowed(loan)

    def test_loan_anuity(self):
        """
        Testing normal workflow
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_01").id,
                10,
                1200.00,
            ))
        loan.action_compute_payment()
        self.assertEqual(
            len(loan.payment_schedule_ids),
            10)
        self.assertEqual(
            loan.total_principle_amount,
            1199.99)
        self.assertEqual(
            loan.total_interest_amount,
            55.70)
        self._workflow_confirm(loan)
        self._workflow_approve(loan)
        self._realized_loan(loan)
        self.assertEqual(
            loan.state,
            "active")
        self.assertEqual(
            loan.employee_id.loan_count,
            1)
        self.assertEqual(
            loan.employee_id.loan_payment_schedule_count,
            10)

        principle_amounts = [
            115.57, 116.53, 117.50, 118.48, 119.47,
            120.46, 121.47, 122.48, 123.50, 124.53,
        ]

        interest_amounts = [
            10.0, 9.04, 8.07, 7.09, 6.10,
            5.10, 4.10, 3.09, 2.07, 1.04,
        ]

        installment_amounts = [
            125.57, 125.57, 125.57, 125.57, 125.57,
            125.56, 125.57, 125.57, 125.57, 125.57,
        ]

        idx = 0
        for schedule in loan.payment_schedule_ids:
            self.assertEqual(
                schedule.principle_amount,
                principle_amounts[idx])
            self.assertEqual(
                schedule.interest_amount,
                interest_amounts[idx])
            self.assertEqual(
                schedule.installment_amount,
                installment_amounts[idx])
            self._pay_principle(schedule)
            self.assertEqual(
                schedule.principle_payment_state,
                "paid")
            self._realize_interest(schedule)
            self._pay_interest(schedule)
            self.assertEqual(
                schedule.interest_payment_state,
                "paid")
            idx += 1
        self.assertEqual(
            loan.state,
            "done")

    def test_loan_flat(self):
        """
        Testing normal workflow
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_02").id,
                10,
                1200.00,
            ))
        loan.action_compute_payment()
        self.assertEqual(
            len(loan.payment_schedule_ids),
            10)
        self.assertEqual(
            loan.total_principle_amount,
            1200.00)
        self.assertEqual(
            loan.total_interest_amount,
            100.00)
        self._workflow_confirm(loan)
        self._workflow_approve(loan)
        self._realized_loan(loan)
        self.assertEqual(
            loan.state,
            "active")

        principle_amounts = [
            120.0, 120.0, 120.0, 120.0, 120.0,
            120.0, 120.0, 120.0, 120.0, 120.0
        ]

        interest_amounts = [
            10.0, 10.0, 10.0, 10.0, 10.0,
            10.0, 10.0, 10.0, 10.0, 10.0,
        ]

        installment_amounts = [
            130.0, 130.0, 130.0, 130.0, 130.0,
            130.0, 130.0, 130.0, 130.0, 130.0,
        ]

        idx = 0
        for schedule in loan.payment_schedule_ids:
            self.assertEqual(
                schedule.principle_amount,
                principle_amounts[idx])
            self.assertEqual(
                schedule.interest_amount,
                interest_amounts[idx])
            self.assertEqual(
                schedule.installment_amount,
                installment_amounts[idx])
            self._pay_principle(schedule)
            self.assertEqual(
                schedule.principle_payment_state,
                "paid")
            self._realize_interest(schedule)
            self._pay_interest(schedule)
            self.assertEqual(
                schedule.interest_payment_state,
                "paid")
            idx += 1

        self.assertEqual(
            loan.state,
            "done")

    def test_loan_effective(self):
        """
        Testing normal workflow
        """
        loan = self.env["hr.loan"].create(
            self._prepare_loan(
                self.env.ref("hr_loan_management.loan_type_03").id,
                10,
                1200.00,
            ))
        loan.action_compute_payment()
        self.assertEqual(
            len(loan.payment_schedule_ids),
            10)
        self.assertEqual(
            loan.total_principle_amount,
            1200.00)
        self.assertEqual(
            loan.total_interest_amount,
            55.00)
        self._workflow_confirm(loan)
        self._workflow_approve(loan)
        self._realized_loan(loan)
        self.assertEqual(
            loan.state,
            "active")

        principle_amounts = [
            120.0, 120.0, 120.0, 120.0, 120.0,
            120.0, 120.0, 120.0, 120.0, 120.0,
        ]

        interest_amounts = [
            10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0,
            3.0, 2.0, 1.0,
        ]

        installment_amounts = [
            130.0, 129.0, 128.0, 127.0, 126.0,
            125.0, 124.0, 123.0, 122.0, 121.0,
        ]
        idx = 0
        for schedule in loan.payment_schedule_ids:
            self.assertEqual(
                schedule.principle_amount,
                principle_amounts[idx])
            self.assertEqual(
                schedule.interest_amount,
                interest_amounts[idx])
            self.assertEqual(
                schedule.installment_amount,
                installment_amounts[idx])
            self._pay_principle(schedule)
            self.assertEqual(
                schedule.principle_payment_state,
                "paid")
            self._realize_interest(schedule)
            self._pay_interest(schedule)
            self.assertEqual(
                schedule.interest_payment_state,
                "paid")
            idx += 1
        self.assertEqual(
            loan.state,
            "done")
