from odoo import fields, models, _


class HrEmployeeBenefitCategory(models.Model):
    """Employee Benefit Category"""

    _name = 'hr.employee.benefit.category'
    _description = _(__doc__)

    name = fields.Char(string='Benefit Name', required=True)
    code = fields.Char(
        string='Code',
        help="The code that can be used in the salary rules to identify "
        "the benefit",
    )
    description = fields.Text(
        string='Description',
        help="Brief explanation of which benefits the category contains."
    )
    salary_rule_ids = fields.Many2many(
        comodel_name='hr.salary.rule',
        relation='salary_rule_employee_benefit_rel',
        column1='benefit_id', column2='salary_rule_id', string='Salary Rules',
    )
    rate_ids = fields.One2many(
        comodel_name='hr.employee.benefit.rate',
        inverse_name='category_id',
        string="Benefit Rates",
    )
    reference = fields.Char(
        string='Reference',
        help="Field used to enter an external identifier for a "
        "benefit category. Example, pension plans may have a "
        "registration number."
    )
    active = fields.Boolean(string='active', default=True)
