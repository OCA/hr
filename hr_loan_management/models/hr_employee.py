# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    @api.depends(
        "loan_ids",
        "payment_schedule_ids")
    def _compute_loan(self):
        obj_loan = self.env["hr.loan"]
        obj_schedule = self.env["hr.loan.payment.schedule"]
        for employee in self:
            criteria = [
                ("employee_id", "=", employee.id),
            ]
            loan_criteria = [
                ("state", "in", ["active", "done"])
            ] + criteria
            self.loan_count = obj_loan.search_count(
                loan_criteria)
            schedule_criteria = [
                ("loan_id.state", "in", ["active", "done"])
            ] + criteria
            self.loan_payment_schedule_count = \
                obj_schedule.search_count(
                    schedule_criteria)

    loan_ids = fields.One2many(
        string="Loan(s)",
        comodel_name="hr.loan",
        inverse_name="employee_id",
    )
    payment_schedule_ids = fields.One2many(
        string="Loan Repayment Schedule(s)",
        comodel_name="hr.loan.payment.schedule",
        inverse_name="employee_id",
    )
    loan_count = fields.Integer(
        string="Loan Count",
        compute="_compute_loan",
    )
    loan_payment_schedule_count = fields.Integer(
        string="Loan Repayment Schedule Count",
        compute="_compute_loan",
    )
