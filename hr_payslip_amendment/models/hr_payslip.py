#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, models

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @staticmethod
    def _input_line_by_code(lines, contract_ids):
        map = dict.fromkeys(contract_ids, {})
        count = 0
        for line in lines:
            map[line['contract_id']][line['code']] = count
            count += 1
        return map
    
    @api.multi
    def reset_amendments(self):
        amendments = self.env['hr.apyslip.amendment'].\
                                search([('slip_id', 'in', self.ids), 
                                        ('state', '=', 'done')])
        amendments.write({'slip_id' : None, 'state' : 'validate'})
                                
        
    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        '''
        overrides get_input to add our amendments... amendments are only added
        if the salary rule structure has rules that have the input code
        '''
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        input_map = self._input_line_by_code(res, contract_ids)
        contracts = self.env['hr.contract'].browse(contract_ids)
        # let's get all payslips amendments affecting contracts in this batch
        amendment_pool = self.env['hr.payslip.amendment']
        employee_ids = [contract.employee_id.id for contract in contracts]
        amendments = amendment_pool.search([('state', '=', 'validate'),
                                           ('date', '>=', date_from),
                                           ('date', '<', date_to),
                                           ('employee_id', 'in', employee_ids)])
        
        for contract in contracts:
            for amendment in amendments:
                code = amendment.input_id.code
                if code in input_map[contract.id]:
                    res[input_map[contract.id][code]]['amount'] = amendment.amount
        return res

    @api.multi
    def unlink(self):
        self.reset_amendments()
        return super(HrPayslip, self).unlink()
    
    @api.multi
    def cancel_sheet(self):
        self.reset_amendments()
        return super(HrPayslip, self).cancel_sheet()
    
    @api.multi
    def process_sheet(self):
        super(HrPayslip, self).process_sheet()
        for slip in self:
            for input in self.input_line_ids:
                if input.amount > 0:     
                    input_rule = self.env['hr.rule.input'].search([('code', '=', input.code)])     
                    amendments = self.env['hr.payslip.amendment'] \
                        .search([('state', '=', 'validate'),
                                   ('date', '>=', slip.date_from),
                                   ('date', '<', slip.date_to),
                                   ('employee_id', '=', slip.employee_id.id),
                                   ('input_id', '=', input_rule.id)])
                    amendments.write({'state' : 'done', 'slip_id' : slip.id})

    