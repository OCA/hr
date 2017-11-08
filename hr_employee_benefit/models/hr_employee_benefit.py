from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .hr_employee_benefit_rate import get_amount_types


class HrEmployeeBenefit(models.Model):
    """Employee Benefit"""

    _name = 'hr.employee.benefit'
    _description = _(__doc__)

    contract_id = fields.Many2one(
        comodel_name='hr.contract',
        string='Contract',
        ondelete='cascade',
        index=True,
    )
    category_id = fields.Many2one(
        comodel_name='hr.employee.benefit.category',
        string='Benefit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    rate_id = fields.Many2one(
        comodel_name='hr.employee.benefit.rate',
        string='Rate',
        required=True,
    )
    employee_amount = fields.Float(
        related='rate_id.employee_amount',
        string='Employee Amount',
        readonly=True,
    )
    employer_amount = fields.Float(
        related='rate_id.employer_amount',
        string='Employer Amount',
        readonly=True,
    )
    amount_type = fields.Selection(
        get_amount_types,
        related='rate_id.amount_type',
        string="Amount Type",
        readonly=True,
    )
    date_start = fields.Date(
        string='Start Date', required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date(string='End Date')
    code = fields.Char(
        related='category_id.code',
        string='Code',
    )

    @api.constrains('category_id', 'rate_id')
    def _check_category_id(self):
        """
        Checks that the category on the benefit and the rate
        is the same
        """
        for record in self:
            if not record.category_id == record.rate_id.category_id:
                raise ValidationError(
                    _('You must select a rate related to the '
                      'selected category.'))

    @api.multi
    def compute_amounts(self, payslip):
        for record in self:
            if (
                record.date_start <= payslip.date_from and
                not (record.date_end and payslip.date_to > record.date_end)
            ):
                record.rate_id.compute_amounts(payslip)
