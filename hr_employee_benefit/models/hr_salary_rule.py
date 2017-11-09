from odoo import api, fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    employee_benefit_ids = fields.Many2many(
        comodel_name='hr.employee.benefit.category',
        relation='salary_rule_employee_benefit_rel',
        column1='salary_rule_id', column2='benefit_id',
        string='Salary Rules',
    )

    @api.multi
    def sum_benefits(self, payslip, **kwargs):
        """
        Method used to sum the employee benefits computed on the payslip

        Because there are many possible parameters and that the module
        needs to be inherited easily, arguments are passed through kwargs

        :param codes: The type of benefit over which to sum
        :type codes: list of string or single string

        :param employer: If True, sum over the employer contribution.
        If False, sum over the employee contribution

        Example
        -------
        payslip.compute_benefits(payslip, employer=True)
        Will return the employer contribution for the pay period
        """
        self.ensure_one()

        benefits = self._filter_benefits(payslip, **kwargs)

        employer = kwargs.get('employer', False)

        if employer:
            res = sum(ben.employer_amount for ben in benefits)
        else:
            res = sum(ben.employee_amount for ben in benefits)

        return res

    @api.multi
    @api.returns('hr.payslip.benefit.line')
    def _filter_benefits(self, payslip, codes=False, **kwargs):
        """
        Filter the benefit records on the payslip
        :rtype: record set of hr.payslip.benefit.line
        """
        self.ensure_one()

        benefits = payslip.benefit_line_ids

        if codes:
            if isinstance(codes, str):
                codes = [codes]

            return benefits.filtered(
                lambda b: b.category_id.code in codes)

        # If the salary rule is linked to no benefit category,
        # by default it accepts every categories.
        if self.employee_benefit_ids:
            return benefits.filtered(
                lambda b: b.category_id in self.employee_benefit_ids)

        return benefits
