# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    language_ids = fields.One2many(
        "hr.employee.language",
        "employee_id",
        string="Languages",
        help="Languages of this employee",
    )
