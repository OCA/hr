from odoo import fields, models


class HRDepartmentCode(models.Model):
    _inherit = 'hr.department'

    code = fields.Char('Department Code')
