# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
 

class hr_payroll_structure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    selectable = fields.Boolean('Can be Assign', default=True,
                    help='Indicates if this salary structure can be assigned '
                    'directly to contracts')
    
