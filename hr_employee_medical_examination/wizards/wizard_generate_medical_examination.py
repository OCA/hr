# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class WizardGenerateMedicalExamination(models.TransientModel):

    _name = 'wizard.generate.medical.examination'

    name = fields.Char(required=True, string='Examination Name')

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employees'
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
    )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job',
    )

    def _prepare_employee_domain(self):
        res = []
        if self.job_id:
            res.append(('job_id', '=', self.job_id.id))
        if self.department_id:
            res.append(('department_id', 'child_of', self.department_id.id))
        return res

    @api.multi
    def populate(self):
        domain = self._prepare_employee_domain()
        employees = self.env['hr.employee'].search(domain)
        self.employee_ids = employees
        action = {
            'name': _('Generate Medical Examinations'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.generate.medical.examination',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context,
        }
        return action

    def _create_examination_vals(self, employee):
        return {
            'name':  _('%s on %s') % (self.name, employee.name),
            'employee_id': employee.id,
        }

    @api.multi
    def create_medical_examinations(self):
        exams = self.env['hr.employee.medical.examination']
        for form in self:
            for employee in form.employee_ids:
                exams |= self.env['hr.employee.medical.examination'].create(
                    form._create_examination_vals(employee)
                )
        action = self.env.ref(
            'hr_employee_medical_examination.hr_employee'
            '_medical_examination_act_window',
            False
        )
        result = action.read()[0]
        result['domain'] = [('id', 'in', exams.ids)]
        return result
