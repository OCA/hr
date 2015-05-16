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

from openerp.addons.hr_employee_benefit.tests.test_employee_benefit import (
    TestEmployeeBenefitBase)


class TestEmployeeBenefit(TestEmployeeBenefitBase):

    def setUp(self):
        super(TestEmployeeBenefit, self).setUp()
        cr, uid, context = self.cr, self.uid, self.context

        self.rate_model.write(cr, uid, [self.rate_ids[1]], {
            'amount_type': 'percent_gross',
            'line_ids': [(5, 0)],
        }, context=context)

        self.rate_line_ids = [
            self.rate_line_model.create(cr, uid, {
                'parent_id': line[0],
                'employee_amount': line[1],
                'employer_amount': line[2],
                'date_start': line[3],
                'date_end': line[4],
            }, context=context)
            for line in [
                (self.rate_ids[1], 2, 3, '2015-01-01', '2015-06-30'),
                (self.rate_ids[1], 4, 5, '2015-07-01', False),
            ]
        ]

        self.rule_model.write(cr, uid, [self.rule_id], {
            'amount_python_compute': """
payslip.set_gross_salary(payslip, 2000)
payslip.compute_benefits(payslip)
result = rule.sum_benefits(payslip)
"""
        }, context=context)

    def test_compute_payslip(self):
        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20 + 2000 * 2 / 100)
        self.assertEqual(payslip['RULE_2'], 2000 * 3 / 100)
