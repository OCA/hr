# -*- coding:utf-8 -*-
from openerp import models, fields, api, _


class print_run_contrib_register(models.TransientModel):
    _name = 'print.run.contrib_register'
    _description = 'Print Contribution Register'

    contrib_register_ids = fields.Many2many(
                                            'hr.contribution.register',
                                            string="Contribution Registers"
                                            )
    
    @api.multi
    def print_contrib_register(self):
        self.ensure_one()
        run_id = self.env.context['active_id']
        run = self.env['hr.payslip.run'].browse(run_id)

        datas = {
             'model': 'hr.contribution.register', 
             'ids'  : self.contrib_register_ids.ids,
             'form' : {
                       'date_from': run.date_start,
                       'date_to'  : run.date_end,
                       'slip_ids' : run.slip_ids.ids,
                       }
         }
        report_obj = self.env['report'].with_context(active_ids=self.contrib_register_ids.ids,
                                                     active_model='hr.contribution.register')
        return report_obj.get_action(self.contrib_register_ids, 'hr_payroll_report_contrib_register.report_contributionregister',
                                     data=datas)
 