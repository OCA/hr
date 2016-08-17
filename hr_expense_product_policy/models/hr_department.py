# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


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
            category_ids = dept.allowed_expense_product_categ_ids.ids
            criteria = [
                ("categ_id", "in", category_ids),
                ("hr_expense_ok", "=", True),
            ]
            products += obj_product.search(criteria)
            dept.all_allowed_expense_product_ids = products

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
