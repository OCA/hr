# -*- coding: utf-8 -*-
import operator
from openerp import models, fields, api, exceptions
 

class hr_employee(models.Model):

    _inherit = 'hr.employee'
    
    contract_id = fields.Many2one('hr.contract', 'urrent Contract', 
                                  help='Latest contract of the employee',
                                  store=True, readonly=True, index=True,
                                  compute='_compute_current_contract')
    first_contract_id = fields.Many2one('hr.contract', 'Contract',
                                        store=True,readonly=True,
                                        compute='_compute_first_contract')
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, store=True,
                             related='contract_id.job_id')
    
    @api.one 
    @api.depends('contract_ids', 'contract_ids.date_start', 
                 'contract_ids.employee_id', 'contract_ids.job_id')
    def _compute_first_contract(self):
        if len(self.contract_ids):
            contracts_sorted = self.contract_ids\
                        .sorted(key=operator.itemgetter('date_start', 'id'))
            self.first_contract_id = contracts_sorted[0]
        
    @api.one 
    @api.depends('contract_ids', 'contract_ids.date_start', 
                 'contract_ids.employee_id', 'contract_ids.job_id')
    def _compute_current_contract(self):
        if len(self.contract_ids):
            contracts_sorted = self.contract_ids\
                        .sorted(key=operator.itemgetter('date_start', 'id'))
            self.contract_id = contracts_sorted[-1]    