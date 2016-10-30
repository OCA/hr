# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import api, models, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class HrCreatePaymentOrderFromPayslip(models.TransientModel):
    _name = "hr.create_payment_order_from_payslip"
    _description = "Create Payment Order From Payslip"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=_default_company_id,
        )
    bank_cash = fields.Selection(
        string="Bank/Cash?",
        selection=[
            ("bank", "Bank"),
            ("cash", "Cash"),
            ],
        required=True,
        default="bank",
        )
    bank_id = fields.Many2one(
        string="Bank",
        comodel_name="res.bank",
        )
    mode_id = fields.Many2one(
        string="Payment Mode",
        comodel_name="payment.mode",
        required=True,
        )
    date_prefered = fields.Date(
        string="Payment Date",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d"),
        )


    @api.onchange("bank_cash", "bank_id")
    def onchange_bank_cash(self):
        self.mode_id = False
        if self.bank_cash == "cash":
            self.bank_id = False
        if self.bank_cash == "bank":
            domain = [
                ("journal.type", "=", "bank"),
                ("bank_id.bank", "=", self.bank_id.id),
                ("company_id", "=", self.company_id.id),
                ]
        else:
            domain = [
                ("journal.type", "=", "cash"),
                ("company_id", "=", self.company_id.id),
                ]
        return {"domain": {"mode_id": domain}}

    @api.multi
    def action_create(self):
        self.ensure_one()
        self._create_payment_order()

    @api.multi
    def _create_payment_order(self):
        self.ensure_one()
        payslip_ids = self.env.context.get("active_ids", [])
        if len(payslip_ids) == 0:
            strWarning = _("No payslip selected")
            raise UserError(strWarning)
        obj_payment = self.env[
            "payment.order"]
        obj_payslip = self.env[
            "hr.payslip_to_payment_order"]
        payment = obj_payment.create(
            self._prepare_payment_order())
        for payslip in obj_payslip.browse(payslip_ids):
            payslip._create_payslip_line(payment)

    @api.multi
    def _prepare_payment_order(self):
        self.ensure_one()
        res = {
            "date_scheduled": self.date_prefered,
            "mode": self.mode_id.id,
            "user_id": self.mode_id.journal.user_id.id,
            "date_prefered": "fixed",
            }
        return res
