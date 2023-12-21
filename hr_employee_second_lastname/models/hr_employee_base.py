from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    firstname = fields.Char("First name")
    lastname = fields.Char("Last name")
    lastname2 = fields.Char("Second last name")
