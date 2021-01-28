# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.multi
    def action_submit_expenses(self):
        for rec in self:
            if (
                rec.product_id.expense_receipt_required and not rec.attachment_number
            ) and not rec.sheet_id.allow_without_attachment:
                raise UserError(
                    _("You need to provide a receipt to submit this expense!")
                )
        return super(HrExpense, self).action_submit_expenses()


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    allow_without_attachment = fields.Boolean(
        default=False, string="Allow lines without attachment"
    )

    @api.multi
    def action_submit_sheet(self):
        for rec in self:
            for expense in rec.expense_line_ids:
                if (
                    expense.product_id.expense_receipt_required
                    and not expense.attachment_number
                ) and not rec.allow_without_attachment:
                    raise UserError(
                        _("You need to provide a receipt to submit %s expense!")
                        % expense.name
                    )

        return super(HrExpenseSheet, self).action_submit_sheet()
