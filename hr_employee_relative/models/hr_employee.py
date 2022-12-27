# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    relative_ids = fields.One2many(
        comodel_name="hr.employee.relative",
        inverse_name="employee_id",
    )
