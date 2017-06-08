# -*- coding: utf-8 -*-
from openerp import fields, models, api

class human_resources_configuration(models.TransientModel):
    _inherit = 'hr.config.settings'

    default_trial_length = fields.Integer(help="Length is days of trail")
        
    def get_default_default_trial_length(self, cr, uid, ids, context=None):
        res = self.pool["ir.config_parameter"]\
        .get_param(cr, uid, "hr_contract.default_trial_length", 
                   context=context)
        return {'default_trial_length' : res and int(res) or False}
    
    def set_default_trial_length(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        self.pool["ir.config_parameter"]\
            .set_param(cr, uid, "hr_contract.default_trial_length", 
                       config.default_trial_length or None, context=context)
   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: