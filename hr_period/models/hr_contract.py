# -*- coding:utf-8 -*-
# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
