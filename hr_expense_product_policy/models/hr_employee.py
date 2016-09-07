# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.depends(
        "job_id.all_allowed_expense_product_ids",
        "job_id.all_allowed_expense_product_ids.hr_expense_ok",
        "job_id",
        "department_id.all_allowed_expense_product_ids",
        "department_id.all_allowed_expense_product_ids.hr_expense_ok",
        "allowed_expense_product_categ_ids",
        "allowed_expense_product_ids",
        "allowed_expense_product_ids.hr_expense_ok"
    )
    def _compute_all_allowed_product_ids(self):
        obj_product = self.env["product.product"]
        for employee in self:
            products = employee.allowed_expense_product_ids
            category_ids = employee.allowed_expense_product_categ_ids.ids
            criteria = [
                ("categ_id", "in", category_ids),
                ("hr_expense_ok", "=", True),
            ]
            products += obj_product.search(criteria)
            if employee.department_id:
                department = employee.department_id
                products += department.all_allowed_expense_product_ids
            if employee.job_id:
                job = employee.job_id
                products += job.all_allowed_expense_product_ids
            employee.all_allowed_expense_product_ids = products

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        help="""Turn on this options if this employee
    has to choose product when creating expenses"""
    )
    limit_product_selection = fields.Boolean(
        string="Limit Product Selection",
    )
    allowed_expense_product_categ_ids = fields.Many2many(
        string="Allowed Expense Product Categories",
        comodel_name="product.category",
    )
    allowed_expense_product_ids = fields.Many2many(
        string="Allowed Expense Product",
        comodel_name="product.product",
        domain=[("hr_expense_ok", "=", True)],
    )
    all_allowed_expense_product_ids = fields.Many2many(
        string="All Allowed Expense Product",
        comodel_name="product.product",
        compute="_compute_all_allowed_product_ids",
        store=True,
    )
