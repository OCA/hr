from odoo import fields, models


class Leave(models.Model):
    _inherit = "hr.leave"

    contract_id = fields.Many2one("hr.contract", string="Contract")
    percent = fields.Float(help="40.0 means 40 percent leave, 60 percent work")
