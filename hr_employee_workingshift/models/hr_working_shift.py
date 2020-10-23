from odoo import api, fields, models

class HRWorkingShift(models.Model):
    _name = "hr.workingshift"
    _description = "Working Shift"
    _order = "company_id, code"

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    code = fields.Char('Shift Code', required=True)
    name = fields.Char('Shift Name', required=True)
    active = fields.Boolean('Active', default=True)

class Employee(models.Model):
    _inherit = 'hr.employee'

    shift_id = fields.Many2one('hr.workingshift', 'Working Shift')
