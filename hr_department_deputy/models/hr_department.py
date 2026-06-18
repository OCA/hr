# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Department(models.Model):
    _inherit = "hr.department"

    deputy_manager_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="department_deputy_rel",
        column1="department_id",
        column2="employee_id",
        string="Deputy Managers",
        check_company=True,
    )
