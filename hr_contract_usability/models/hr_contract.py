# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta

from openerp import fields, models, _, api

        
class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    @api.onchange('trial_date_start')
    @api.one
    def onchange_trial_date_start(self):        
        if self.trial_date_start:
            res = self.env["ir.config_parameter"]\
                      .get_param("hr_contract.default_trial_length")
            res = res and int(res) or 60
            end_dt = fields.Date.from_string(self.trial_date_start) \
                                + relativedelta(days=res)
            self.trial_date_end = fields.Date.to_string(end_dt)  