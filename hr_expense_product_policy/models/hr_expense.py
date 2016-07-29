# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


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
        relation="rel_all_allowed_product_2_expense",
        column1="expense_id",
        column2="product_id",
        compute="_compute_all_allowed_product_ids",
        store=False,
    )

    @api.onchange("employee_id")
    def onchange_employee(self):
        self.required_expense_product = \
            self.employee_id.required_expense_product
        self.limit_product_selection = \
            self.employee_id.limit_product_selection

    @api.model
    def create(self, vals):
        obj_employee = self.env["hr.employee"]
        employee_id = vals.get("employee_id")
        employee = obj_employee.browse([employee_id])[0]
        product_required = vals.get("required_expense_product", False)
        limit_product = vals.get("limit_product_selection", False)
        if vals.get("line_ids", False):
            for line in map(lambda x: x[2], vals.get("line_ids")):
                product_id = line.get("product_id", False)

                # check required product
                if not product_id and product_required:
                    strWarning = "Product has to be filled"
                    raise models.ValidationError(strWarning)

                # check allowed product
                product_ids = employee.all_allowed_expense_product_ids.ids
                if product_id and limit_product:
                    if product_id not in product_ids:
                        strWarning = "Product is not allowed"
                        raise models.ValidationError(strWarning)

        return super(HrExpense, self).create(vals)

    @api.multi
    def write(self, vals):
        for exp in self:
            if not vals.get("line_ids", False):
                continue

            product_required = vals.get(
                "required_expense_product",
                False) and \
                vals.get("required_expense_product") or \
                exp.required_expense_product

            for line in map(lambda x: x[2], vals.get("line_ids")):
                product_id = line.get("product_id", False)

                # check required product
                if not product_id and product_required:
                    strWarning = "Product has to be filled"
                    raise models.ValidationError(strWarning)

                employee = exp.employee_id
                product_ids = employee.all_allowed_expense_product_ids.ids
                if product_id and exp.limit_product_selection:
                    if product_id not in product_ids:
                        strWarning = "Product is not allowed"
                        raise models.ValidationError(strWarning)

        return super(HrExpense, self).write(vals)


class HrExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        related="expense_id.required_expense_product",
        store=True,
    )
