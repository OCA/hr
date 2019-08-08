# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from .hr_fiscal_year import get_schedules


class HrPayslipEmployees(models.TransientModel):

    _inherit = 'hr.payslip.employees'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True
    )
    schedule_pay = fields.Selection(
        get_schedules,
        'Scheduled Pay',
        readonly=True
    )
