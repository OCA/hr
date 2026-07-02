from odoo import fields, models


class HrEmployeeVcardLayout(models.Model):
    _name = "hr.employee.vcard.layout"
    _description = "Employee vCard Layout"
    _order = "sequence"

    sequence = fields.Integer(default=50)
    name = fields.Char(required=True)
    view_id = fields.Many2one(
        comodel_name="ir.ui.view",
        string="vCard View",
        required=True,
        domain=[("type", "=", "qweb")],
    )
