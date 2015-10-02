# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    employee_benefit_ids = fields.Many2many(
        'hr.employee.benefit.category',
        'salary_rule_employee_benefit_rel',
        'salary_rule_id', 'benefit_id', 'Salary Rules',
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

        Exemple
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
        """ Filter the benefit records on the payslip
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
