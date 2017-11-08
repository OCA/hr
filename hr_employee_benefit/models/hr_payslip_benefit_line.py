from odoo import fields, models, _

import odoo.addons.decimal_precision as dp


class HrPayslipBenefitLine(models.Model):
    """Pay Slip Employee Benefit Line"""

    _name = 'hr.payslip.benefit.line'
    _description = _(__doc__)

    payslip_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip',
        required=True,
        ondelete='cascade',
    )
    category_id = fields.Many2one(
        comodel_name='hr.employee.benefit.category',
        string='Benefit',
        required=True,
    )
    employer_amount = fields.Float(
        string='Employer Contribution',
        digits_compute=dp.get_precision('Payroll'),
    )
    employee_amount = fields.Float(
        string='Employee Contribution',
        digits_compute=dp.get_precision('Payroll'),
    )
    source = fields.Selection(
        [
            ('contract', 'From Contract'),
            ('manual', 'Added Manually'),
        ],
        readonly=True,
        required=True,
        string='Type',
        type='char',
        default='manual',
    )
    reference = fields.Char(string='Reference')
