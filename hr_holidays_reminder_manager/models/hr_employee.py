from odoo import models, fields


class HREmployee(models.Model):
    _inherit = "hr.employee"

    hr_manager = fields.Boolean(string="Is a HR Manager")
