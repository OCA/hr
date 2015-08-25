# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
#

import random
import string
from openerp import models, fields, api, _
from openerp.exceptions import Warning

class HrEmployee(models.Model):
    """Implement company wide unique identification number."""    
    
    _inherit = 'hr.employee'  
    

    employee_no = fields.Char('Employee ID', required=False,
                       readonly=True, copy=False, default='/')


    _sql_constraints = [
        ('employeeno_uniq', 'unique(employee_no)', 'The Employee Number must be unique across the company(s).'),
    ]
    
    @api.model
    def _generate_employeeno(self):
        """Generate a random employee identification number"""
        config_obj = self.env["ir.config_parameter"]
        employee_id_gen_method  =  config_obj.get_param("hr_employee_id.employee_id_gen_method")
        if not employee_id_gen_method:
            raise Warning('Please specify a Employee ID generation method in HR Configuration')
        employee_id = False
        if employee_id_gen_method == 'sequence':
            employee_id_sequence =  config_obj.get_param("hr_employee_id.employee_id_sequence")
            if not employee_id_sequence:
                raise Warning('Please specify a Employee ID generation sequence in HR Configuration')
            employee_id = self.env['ir.sequence'].next_by_id(int(employee_id_sequence))
        elif employee_id_gen_method == 'random':            
            employee_id_random_digits =  int(config_obj.get_param("hr_employee_id.employee_id_random_digits"))
            if not employee_id_random_digits:
                raise Warning('Please specify Employee ID digit length in HR Configuration')
            tries = 0
            max_tries = 50
            while tries < max_tries:
                rnd = random.SystemRandom()
                employee_id = ''.join(rnd.choice(string.digits)
                              for _ in xrange(employee_id_random_digits))
                self.env.cr.execute(
                    '''SELECT employee_no FROM hr_employee WHERE employee_no=%s''', tuple((employee_id,)))
                res = self.env.cr.fetchall()
                if len(res) == 0:
                    break
                tries += 1    
            if tries == max_tries:
                raise Warning(_('Unable to generate an Employee ID number that is unique.'))       
        return employee_id
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        eid = self._generate_employeeno()
        vals['employee_no'] = eid
        vals['identification_id'] = eid
        return super(HrEmployee, self).create(vals)
