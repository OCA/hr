from odoo import fields, models, _

import odoo.addons.decimal_precision as dp

from .hr_employee_benefit_rate import get_amount_types


class HrEmployeeBenefitRateLine(models.Model):
    """Employee Benefit Rate Line"""

    _name = 'hr.employee.benefit.rate.line'
    _description = _(__doc__)

    employee_amount = fields.Float(
        string='Employee Amount',
        required=True,
        digits_compute=dp.get_precision('Payroll'),
    )
    employer_amount = fields.Float(
        string='Employer Amount',
        required=True,
        digits_compute=dp.get_precision('Payroll'),
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date('End Date')
    parent_id = fields.Many2one(
        comodel_name='hr.employee.benefit.rate',
        string='Parent',
        ondelete='cascade',
        required=True,
    )
    amount_type = fields.Selection(
        get_amount_types,
        related='parent_id.amount_type',
        string="Amount Type",
        readonly=True,
    )
    category_id = fields.Many2one(
        comodel_name='hr.employee.benefit.category',
        related='parent_id.category_id',
        string="Category",
        readonly=True,
    )

    _order = 'date_start desc'
