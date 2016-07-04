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
            category_ids = employee.allowed_expense_product_categ_ids.mapped(
                "id")
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

            employee.all_allowed_expense_product_ids = \
                products.mapped("id")

    required_expense_product = fields.Boolean(
        string="Required Expense Product",
        default=False,
        help="""Turn on this options if this employee
    has to choose product when creating expenses"""
        )
    allowed_expense_product_categ_ids = fields.Many2many(
        string="Allowed Expense Product Categories",
        comodel_name="product.category",
        relation="rel_allowed_product_categ_2_employee",
        column1="employee_id",
        column2="product_categ_id"
    )
    allowed_expense_product_ids = fields.Many2many(
        string="Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_allowed_product_2_employee",
        column1="employee_id",
        column2="product_id",
        domain=[("hr_expense_ok", "=", True)],
    )
    all_allowed_expense_product_ids = fields.Many2many(
        string="All Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_all_allowed_product_2_employee",
        column1="employee_id",
        column2="product_id",
        compute="_compute_all_allowed_product_ids",
        store=True,
    )


class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.depends(
        "allowed_expense_product_categ_ids",
        "allowed_expense_product_ids",
        "allowed_expense_product_ids.hr_expense_ok")
    def _compute_all_allowed_product_ids(self):
        obj_product = self.env["product.product"]
        for dept in self:
            products = dept.allowed_expense_product_ids
            category_ids = dept.allowed_expense_product_categ_ids.mapped(
                "id")
            criteria = [
                ("categ_id", "in", category_ids),
                ("hr_expense_ok", "=", True),
                ]
            products += obj_product.search(criteria)
            dept.all_allowed_expense_product_ids = \
                products.mapped("id")

    allowed_expense_product_categ_ids = fields.Many2many(
        string="Allowed Expense Product Categories",
        comodel_name="product.category",
        relation="rel_allowed_product_categ_2_dept",
        column1="department_id",
        column2="product_categ_id"
    )
    allowed_expense_product_ids = fields.Many2many(
        string="Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_allowed_product_2_dept",
        column1="department_id",
        column2="product_id",
        domain=[("hr_expense_ok", "=", True)],
    )
    all_allowed_expense_product_ids = fields.Many2many(
        string="All Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_all_allowed_product_2_dept",
        column1="department_id",
        column2="product_id",
        compute="_compute_all_allowed_product_ids",
        store=True,
    )


class HrJob(models.Model):
    _inherit = "hr.job"

    @api.depends(
        "allowed_expense_product_categ_ids",
        "allowed_expense_product_ids",
        "allowed_expense_product_ids.hr_expense_ok")
    def _compute_all_allowed_product_ids(self):
        obj_product = self.env["product.product"]
        for job in self:
            products = job.allowed_expense_product_ids
            category_ids = job.allowed_expense_product_categ_ids.mapped(
                "id")
            criteria = [
                ("categ_id", "in", category_ids),
                ("hr_expense_ok", "=", True),
                ]
            products += obj_product.search(criteria)
            job.all_allowed_expense_product_ids = \
                products.mapped("id")

    allowed_expense_product_categ_ids = fields.Many2many(
        string="Allowed Expense Product Categories",
        comodel_name="product.category",
        relation="rel_allowed_product_categ_2_job",
        column1="job_id",
        column2="product_categ_id"
    )
    allowed_expense_product_ids = fields.Many2many(
        string="Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_allowed_product_2_job",
        column1="job_id",
        column2="product_id",
        domain=[("hr_expense_ok", "=", True)],
    )
    all_allowed_expense_product_ids = fields.Many2many(
        string="All Allowed Expense Product",
        comodel_name="product.product",
        relation="rel_all_allowed_product_2_job",
        column1="job_id",
        column2="product_id",
        compute="_compute_all_allowed_product_ids",
        store=True,
    )
