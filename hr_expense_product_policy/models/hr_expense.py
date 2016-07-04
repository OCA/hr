# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools import ustr


class HrExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.depends(
        "employee_id",
        "employee_id.required_expense_product")
    def _compute_required_expense_product(self):
        for expense in self:
            expense.required_expense_product = \
                expense.employee_id.required_expense_product

    @api.depends(
        "employee_id",
        "employee_id.all_allowed_expense_product_ids")
    def _compute_all_allowed_product_ids(self):
        for expense in self:
            expense.all_allowed_expense_product_ids = \
                expense.employee_id.all_allowed_expense_product_ids.mapped(
                    "id")

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        compute="_compute_required_expense_product",
        store=True,
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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Inject the domain here to avoid conflicts with other modules.
        product_tmpl_id field will only be present when sale_order_variants
        is installed.
        """
        res = super(HrExpense, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != "form":
            return res
        domain_dict = {
            "product_id":
                "('id', 'in', parent.all_allowed_expense_product_ids[0][2]), ",
        }
        if "line_ids" not in res["fields"]:
            return res
        line_field = res["fields"]["line_ids"]
        for view_type, view in line_field["views"].iteritems():
            if view_type not in ("tree", "form"):
                continue
            for field_name, domain_field in domain_dict.iteritems():
                if field_name not in view["fields"]:
                    continue
                field = view["fields"][field_name]
                domain = ustr(field.get("domain", "[]"))
                field["domain"] = domain[:1] + domain_field + domain[1:]
        return res


class HrExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    @api.depends(
        "expense_id",
        "expense_id.required_expense_product",
        )
    def _compute_required_expense_product(self):
        for line in self:
            line.required_expense_product = \
                line.expense_id.required_expense_product

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        compute="_compute_required_expense_product",
        store=True,
        )
