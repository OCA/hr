# -*- coding: utf-8 -*-
# © 2016 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class HrPayslipLine(models.Model):

    _inherit = 'hr.payslip.line'

    amount_ytd = fields.Float(
        'Total YTD',
        digits_compute=dp.get_precision('Payroll'),
    )
