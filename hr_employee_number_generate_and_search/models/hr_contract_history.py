from odoo import fields, models


class ContractHistory(models.Model):
    _inherit = "hr.contract.history"

    employee_number = fields.Char(
        "Employee Number", related="employee_id.employee_number", readonly=True
    )
