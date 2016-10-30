# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools import drop_view_if_exists


class HrPayslipToPaymentOrder(models.Model):
    _name = "hr.payslip_to_payment_order"
    _description = "Payslip to Payment Order"
    _auto = False

    @api.multi
    def _compute_payment(self):
        for payslip in self:
            payslip.payment_on_progress = 0
            payslip.amount_payment_on_progress = 0.0
            payslip.amount_paid = payslip.amount
            for payment in payslip.payment_order_line_ids:
                line = payment.move_line_id
                if line.reconcile_id or line.reconcile_partial_id:
                    payslip.amount_paid -= line.amount_residual
                    continue

                if payment.order_id.state in ["draft", "open"]:
                    payslip.payment_on_progress += 1
                    payslip.amount_payment_on_progress += payment.amount

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    description = fields.Char(
        string="Description",
    )
    payslip_id = fields.Many2one(
        string="Payslip",
        comodel_name="hr.payslip",
    )
    payslip_number = fields.Char(
        string="# Payslip",
    )
    date_payslip = fields.Date(
        string="Payslip Date",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    amount = fields.Float(
        string="Amount",
    )
    move_line_id = fields.Many2one(
        string="Move Line",
        comodel_name="account.move.line",
    )
    bank_id = fields.Many2one(
        string="Bank",
        comodel_name="res.bank",
    )
    partner_bank_id = fields.Many2one(
        string="Partner's Bank Account",
        comodel_name="res.partner.bank",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial"),
            ("paid", "Paid"),
        ],
    )
    payment_order_line_ids = fields.One2many(
        string="Payment Order Lines",
        comodel_name="payment.line",
        inverse_name="move_line_id",
    )
    payment_on_progress = fields.Integer(
        string="Payment on Progress",
        compute="_compute_payment",
    )
    amount_payment_on_progress = fields.Float(
        sring="Amount on Progress",
        compute="_compute_payment",
    )
    amount_paid = fields.Float(
        sring="Amount Paid",
        compute="_compute_payment",
    )

    def init(self, cr):
        drop_view_if_exists(cr, "hr_payslip_to_payment_order")
        strSQL = """
                    CREATE OR REPLACE VIEW hr_payslip_to_payment_order AS (
                        SELECT  c.id AS id,
                                a.id AS payslip_id,
                                a.company_id AS company_id,
                                c.name AS description,
                                b.date AS date_payslip,
                                a.number AS payslip_number,
                                a.employee_id AS employee_id,
                                c.partner_id AS partner_id,
                                c.credit AS amount,
                                c.id AS move_line_id,
                                i.id AS bank_id,
                                g.bank_account_id AS partner_bank_id,
                                CASE
                                    WHEN
                                        c.reconcile_id IS NOT NULL
                                    THEN
                                        'paid'
                                    WHEN
                                        c.reconcile_partial_id IS NOT NULL
                                    THEN
                                        'partial'
                                    WHEN
                                        c.reconcile_id IS NULL
                                        AND c.reconcile_id IS NULL
                                    THEN
                                        'unpaid'
                                END AS state
                        FROM    hr_payslip AS a
                        JOIN    account_move AS b ON a.move_id = b.id
                        JOIN    account_move_line AS c ON b.id = c.move_id
                        JOIN    account_account AS d ON c.account_id = d.id
                        JOIN    hr_employee AS g ON a.employee_id = g.id
                        LEFT JOIN   res_partner_bank AS h ON
                            g.bank_account_id = h.id
                        LEFT JOIN   res_bank AS i ON h.bank = i.id
                        WHERE   c.credit > 0.0 AND
                                c.partner_id IS NOT NULL AND
                                d.reconcile = True
                    )
                    """
        cr.execute(strSQL)

    @api.multi
    def _create_payslip_line(self, payment):
        self.ensure_one()
        obj_line = self.env[
            "payment.line"]
        obj_line.create(
            self._prepare_payslip_line(payment))

    @api.multi
    def _prepare_payslip_line(self, payment):
        self.ensure_one()
        obj_line = self.env[
            "payment.line"]
        line = self.move_line_id
        if not line.currency_id:
            currency = self.company_id.currency_id
        else:
            currency = line.currency
        company_currency_id = obj_line._get_currency()
        res = {
            "move_line_id": self.move_line_id.id,
            "amount_currency": line.amount_residual_currency,
            "currency": currency.id,
            "communication": line.ref,
            "bank_id": self.partner_bank_id.id,
            "company_currency": company_currency_id,
            "order_id": payment.id,
            "date": payment.date_scheduled,
            "state": "normal",
            "partner_id": self.partner_id.id,
        }
        return res
