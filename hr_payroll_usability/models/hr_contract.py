# -*- coding:utf-8 -*-
from openerp import fields, models, _, api
from dateutil.relativedelta import relativedelta

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    
    @api.model
    def _get_struct_id(self):
        res = self.env["ir.config_parameter"]\
                  .get_param("hr_payroll.default_salary_structure")
        if res:
            return int(res)
    
    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structure', 
                                domain=[('selectable', '=', True)], 
                                default=_get_struct_id)
