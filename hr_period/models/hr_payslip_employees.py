# -*- coding:utf-8 -*-
from openerp import models, fields

from .hr_fiscal_year import get_schedules


class HrPayslipEmployees(models.TransientModel):

    _inherit = 'hr.payslip.employees'

    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    schedule_pay = fields.Selection(get_schedules, 'Scheduled Pay',
                                    readonly=True)
