from odoo import models, fields, api

class HrAppraisalTemplate(models.Model):
    _name = 'hr.appraisal.employee.template'
    _description = 'HR Appraisal Templates'
    _rec_name = 'description'

    description= fields.Text(string='Description', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    appraisal_employee_feedback_template = fields.Html(string='Employee Feedback', translate=True)
    appraisal_manager_feedback_template = fields.Html(string='Manager Feedback', translate=True)
    is_default = fields.Boolean(string='Default Template', default=False)

    @api.model
    def create(self, vals):
        if vals.get('is_default', False):
            self.search([('is_default', '=', True)]).write({'is_default': False})
        return super(HrAppraisalTemplate, self).create(vals)

    def write(self, vals):
        if vals.get('is_default', False):
            self.search([('is_default', '=', True)]).write({'is_default': False})
        return super(HrAppraisalTemplate, self).write(vals)