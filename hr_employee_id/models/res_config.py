# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields, SUPERUSER_ID


class human_resources_configuration(models.TransientModel):
    _inherit = 'hr.config.settings'

    employee_id_gen_method = fields.Selection((('random', 'Random'),
                                               ('sequence', 'Sequence')), string="ID Generation Method", default='random',
                                              help="Method by which employee ID is generated; \
                                              Random - IDs are generated randomly \
                                              Sequence - IDs are generated based on a supplied sequence")
    
    employee_id_random_digits = fields.Integer('# of Digits', default=5, help="Number of digits making up the ID")
    employee_id_sequence = fields.Many2one('ir.sequence', 'Sequence', help="Pattern to be used for used for ID Generation")
    
    def get_default_employee_id_gen_method(self, cr, uid, ids, context=None):
        employee_id_gen_method  = self.pool.get("ir.config_parameter").get_param(cr, uid, "hr_employee_id.employee_id_gen_method", default=None, context=context)
        return {'employee_id_gen_method': employee_id_gen_method  or False}

    def set_employee_id_gen_method (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "hr_employee_id.employee_id_gen_method", record.employee_id_gen_method  or '', context=context)
            
    def get_default_employee_id_random_digits(self, cr, uid, ids, context=None):
        employee_id_random_digits  = self.pool.get("ir.config_parameter").get_param(cr, uid, "hr_employee_id.employee_id_random_digits", default=None, context=context)
        return {'employee_id_random_digits': int(employee_id_random_digits)  or False}

    def set_employee_id_random_digits (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "hr_employee_id.employee_id_random_digits", record.employee_id_random_digits  or '', context=context)
            
    def get_default_employee_id_sequence(self, cr, uid, ids, context=None):
        employee_id_sequence  = self.pool.get("ir.config_parameter").get_param(cr, uid, "hr_employee_id.employee_id_sequence", default=None, context=context)
        if not employee_id_sequence:
            dataobj = self.pool.get('ir.model.data')
            try:
                dummy, employee_id_sequence = dataobj.get_object_reference(cr, SUPERUSER_ID, 'hr_employee_id', 'seq_employeeid_ref')
            except ValueError:
                pass
        return {'employee_id_sequence': int(employee_id_sequence)  or False}

    def set_employee_id_sequence (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "hr_employee_id.employee_id_sequence", record.employee_id_sequence.id  or '', context=context)