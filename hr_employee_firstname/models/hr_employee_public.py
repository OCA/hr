# Copyright 2026 Studio73 (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    firstname = fields.Char(related="employee_id.firstname")
    lastname = fields.Char(related="employee_id.lastname")
