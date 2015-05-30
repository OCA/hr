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

from openerp.osv import fields, orm


class HrSalaryRule(orm.Model):
    _inherit = 'hr.salary.rule'

    _columns = {
        'employee_benefit_ids': fields.many2many(
            'hr.employee.benefit.category', 'salary_rule_employee_benefit_rel',
            'salary_rule_id', 'benefit_id', 'Salary Rules',
        ),
    }

    def sum_benefits(self, cr, uid, ids, payslip, context=None, **kwargs):
        """
        Method used to sum the employee benefits computed on the payslip

        Because there are many possible parameters and that the module
        needs to be inherited easily, arguments are passed through kwargs

        :param codes: The type of benefit over which to sum
        :type codes: list of string or single string

        Benefit Codes should be used in very specific cases
        Example, you may have a salary rule on which you need to sum
        the employee contribution for a category of benefit
        the employer contribution for another category

        :param employer: If True, sum over the employer contribution.
        If False, sum over the employee contribution
        :type annual: boolean

        Exemple
        -------
        payslip.compute_benefits(payslip, employer=True)
        Will return the employer contribution for the pay period
        """
        if not isinstance(payslip, orm.browse_record):
            payslip = payslip.dict

        payslip.refresh()

        benefits = self._filter_benefits(cr, uid, ids, payslip, **kwargs)

        employer = kwargs.get('employer', False)

        if employer:
            res = sum([ben.employer_amount for ben in benefits])
        else:
            res = sum([ben.employee_amount for ben in benefits])

        return res

    def _filter_benefits(self, cr, uid, ids, payslip, context=None, **kwargs):
        """ Filter the benefit records on the payslip
        :rtype: list of hr.payslip.benefit.line browse records
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert(len(ids) == 1)

        rule = self.browse(cr, uid, ids[0], context=context)

        benefits = payslip.benefit_line_ids
        benefit_codes = kwargs.get('codes', False)

        if benefit_codes:
            if isinstance(benefit_codes, str):
                benefit_codes = [benefit_codes]

            return [
                ben for ben in benefits
                if ben.category_id.code in benefit_codes
            ]

        # If the salary rule is linked to no benefit category,
        # by default it accepts every categories.
        if rule.employee_benefit_ids:
            return [
                ben for ben in benefits
                if ben.category_id in rule.employee_benefit_ids
            ]

        return benefits
