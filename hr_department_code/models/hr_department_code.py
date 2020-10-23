from odoo import api, fields, models

class HRDepartmentCode(models.Model):
    _inherit = 'hr.department'

    code = fields.Char('Department Code')
