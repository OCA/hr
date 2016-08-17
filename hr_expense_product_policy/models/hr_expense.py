# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _


class HrExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.depends(
        "limit_product_selection",
        "employee_id",
        "employee_id.all_allowed_expense_product_ids")
    def _compute_all_allowed_product_ids(self):
        obj_product = self.env["product.product"]
        for expense in self:
            if expense.limit_product_selection:
                expense.all_allowed_expense_product_ids = \
                    expense.employee_id.all_allowed_expense_product_ids
            else:
                criteria = [
                    ("hr_expense_ok", "=", True),
                ]
                expense.all_allowed_expense_product_ids = \
                    obj_product.search(criteria)

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
    )
    limit_product_selection = fields.Boolean(
        string="Limit Product Selection",
    )
    all_allowed_expense_product_ids = fields.Many2many(
        string="All Allowed Expense Product",
        comodel_name="product.product",
        compute="_compute_all_allowed_product_ids",
        store=False,
    )

    @api.onchange("employee_id")
    def onchange_employee(self):
        self.required_expense_product = \
            self.employee_id.required_expense_product
        self.limit_product_selection = \
            self.employee_id.limit_product_selection


class HrExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        related="expense_id.required_expense_product",
        store=True,
    )

    @api.multi
    @api.constrains("product_id", "expense_id")
    def _check_product(self):
        for line in self:
            if line.expense_id.required_expense_product:
                if not line.product_id:
                    strWarning = _("Product has to be filled")
                    raise models.ValidationError(strWarning)
            emp = line.expense_id.employee_id
            product_ids = emp.all_allowed_expense_product_ids.ids
            if line.product_id and line.expense_id.limit_product_selection:
                if line.product_id.id not in product_ids:
                    strWarning = _("Product is not allowed")
                    raise models.ValidationError(strWarning)
