from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    lastname2 = fields.Char(related="employee_id.lastname2")
