# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from dateutil import relativedelta
from datetime import datetime


class HrLoanType(models.Model):
    _name = "hr.loan.type"
    _description = "Employee Loan Type"

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(
        string="Loan Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    decription = fields.Text(
        string="Description",
    )
    interest_method = fields.Selection(
        string="Interest Method",
        selection=[
            ("anuity", "Anuity"),
            ("flat", "Flat"),
            ("effective", "Effective"),
        ],
        required=True,
        default="anuity",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=_default_currency_id,
    )
    interest_amount = fields.Float(
        string="Interest Amount",
    )
    maximum_loan_amount = fields.Float(
        string="Maximum Loan Amount",
        required=True,
    )
    maximum_installment_period = fields.Integer(
        string="Maximum Installment Period",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
    account_realization_id = fields.Many2one(
        string="Realization Account",
        comodel_name="account.account",
    )
    account_interest_id = fields.Many2one(
        string="Interest Account",
        comodel_name="account.account",
    )
    account_interest_income_id = fields.Many2one(
        string="Interest Income Account",
        comodel_name="account.account",
    )
    account_principle_id = fields.Many2one(
        string="Principle Account",
        comodel_name="account.account",
    )

    @api.model
    def _compute_interest(
            self, loan_amount, interest, period,
            first_payment_date, interest_method):
        if interest_method == "flat":
            return self._compute_flat(
                loan_amount, interest, period, first_payment_date)
        elif interest_method == "effective":
            return self._compute_effective(
                loan_amount, interest, period, first_payment_date)
        elif interest_method == "anuity":
            return self._compute_anuity(
                loan_amount, interest, period, first_payment_date)

    @api.model
    def _compute_flat(
            self, loan_amount, interest, period,
            first_payment_date):
        result = []

        principle_amount = loan_amount / period
        interest_amount = (loan_amount *
                           (interest / 100.00)) / 12.0
        next_payment_date = datetime.strptime(first_payment_date,
                                              "%Y-%m-%d")
        for loan_period in range(1, period + 1):
            res = {
                "schedule_date": next_payment_date.strftime("%Y-%m-%d"),
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
            next_payment_date = next_payment_date + \
                relativedelta.relativedelta(
                    months=+1)
        return result

    @api.model
    def _compute_effective(
            self, loan_amount, interest, period,
            first_payment_date):
        result = []
        principle_amount = loan_amount / float(period)
        interest_dec = (interest / 100.00)
        for loan_period in range(1, period + 1):
            period_before = (loan_period - 1)
            interest_amount = (
                loan_amount - (period_before * principle_amount)) * \
                interest_dec / 12.00
            res = {
                "schedule_date": first_payment_date,
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
        return result

    @api.model
    def _compute_anuity(
            self, loan_amount, interest, period,
            first_payment_date):
        result = []
        interest_decimal = (interest / 100.00)
        total_principle_amount = 0.0
        fixed_principle_amount = loan_amount * \
            (
                (interest_decimal / 12.0) /
                (1.0 - (1.0 + (interest_decimal / 12.00))**-float(period)))
        for loan_period in range(1, period + 1):
            interest_amount = (loan_amount - total_principle_amount) * \
                interest_decimal / 12.00
            principle_amount = fixed_principle_amount - interest_amount
            res = {
                "schedule_date": first_payment_date,
                "principle_amount": principle_amount,
                "interest_amount": interest_amount,
            }
            result.append(res)
            total_principle_amount += principle_amount
        return result
