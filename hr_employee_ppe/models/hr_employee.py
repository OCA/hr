# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    """Adds PPE information tab on employees form view."""

    _inherit = "hr.employee"

    ppe_ids = fields.One2many("hr.employee.ppe", "employee_id", "PPEs", help="PPEs")
