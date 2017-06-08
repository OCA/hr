# -*- coding: utf-8 -*-
from openerp import fields, models, api

class human_resources_configuration(models.TransientModel):
    _inherit = 'hr.config.settings'

    default_salary_structure = fields.Many2one('hr.payroll.structure', 
                                               'Default Salary Structure', 
                                          domain=[('selectable', '=', True)])


    def get_default_default_salary_structure(self, cr, uid, ids, context=None):
        res = self.pool["ir.config_parameter"]\
            .get_param(cr, uid, "hr_payroll.default_salary_structure",
                       context=context)
        return {'default_salary_structure': int(res) or False}
    
    def set_default_salary_structure(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids, context)
        self.pool["ir.config_parameter"]\
        .set_param(cr, uid, "hr_payroll.default_salary_structure",
                   config[0].default_salary_structure.id or None,
                   context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: