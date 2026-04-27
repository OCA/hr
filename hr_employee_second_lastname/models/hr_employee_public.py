# Copyright 2026 Vauxoo (<https://www.vauxoo.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    lastname2 = fields.Char(related="employee_id.lastname2")
