# Copyright 2026 APSL-Nagarro, Paloma González-Ripoll Cano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_code = fields.Char(string="Employee Code", copy=False)
