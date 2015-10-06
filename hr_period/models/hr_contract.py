# -*- coding:utf-8 -*-
from openerp import models, fields
from .hr_fiscal_year import get_schedules


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Add semi-monthly to payroll schedules
    shedule_pay = fields.Selection(
                                   get_schedules, 
                                   'Scheduled Pay',
                                   index=True
                                   )