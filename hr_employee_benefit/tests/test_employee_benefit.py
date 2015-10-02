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

from openerp.tests import common


class TestEmployeeBenefitBase(common.TransactionCase):
    """
    This model must not contain any test, only the setUp method, so that
    it can be inherited.
    """
    def setUp(self):
        super(TestEmployeeBenefitBase, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env["res.users"]
        self.contract_model = self.env["hr.contract"]
        self.category_model = self.env["hr.employee.benefit.category"]
        self.benefit_model = self.env["hr.employee.benefit"]
        self.rate_model = self.env["hr.employee.benefit.rate"]
        self.rate_line_model = self.env["hr.employee.benefit.rate.line"]
        self.payslip_model = self.env["hr.payslip"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]

        self.category = self.rule_category_model.search([], limit=1)

        self.rule = self.rule_model.create({
            'name': 'Test 1',
            'sequence': 1,
            'code': 'RULE_1',
            'category_id': self.category.id,
            'amount_select': 'code',
            'amount_python_compute': """
payslip.compute_benefits()
result = rule.sum_benefits(payslip)
"""
        })

        self.rule_2 = self.rule_model.create({
            'name': 'Test 2',
            'sequence': 2,
            'code': 'RULE_2',
            'category_id': self.category.id,
            'amount_select': 'code',
            'amount_python_compute': """
result = rule.sum_benefits(payslip, employer=True)
"""
        })

        self.structure = self.structure_model.create({
            'name': 'TEST',
            'parent_id': False,
            'code': 'TEST',
            'rule_ids': [(6, 0, [self.rule.id, self.rule_2.id])]
        })

        self.employee = self.employee_model.create(
            {'name': 'Employee 1'})

        self.contract = self.contract_model.create({
            'employee_id': self.employee.id,
            'name': 'Contract 1',
            'wage': 50000,
            'struct_id': self.structure.id,
        })

        self.categories = [
            self.category_model.create({
                'name': category[0],
                'description': 'Test',
                'code': category[1],
                'salary_rule_ids': [(6, 0, category[2])],
            })
            for category in [
                ('Category 1', 'BEN_1', [self.rule.id]),
                ('Category 2', 'BEN_2', [self.rule.id, self.rule_2.id]),
            ]
        ]

        self.rates = [
            self.rate_model.create({
                'name': 'Test',
                'category_id': rate[0].id,
                'amount_type': rate[1],
            })
            for rate in [
                (self.categories[0], 'each_pay'),
                (self.categories[1], 'annual'),
            ]
        ]

        self.rate_lines = [
            self.rate_line_model.create({
                'parent_id': line[0].id,
                'employee_amount': line[1],
                'employer_amount': line[2],
                'date_start': line[3],
                'date_end': line[4],
            })
            for line in [
                (self.rates[0], 20, 40, '2015-01-01', '2015-06-30'),
                (self.rates[0], 30, 50, '2015-07-01', False),

                (self.rates[1], 600, 720, '2015-01-01', '2015-06-30'),
                (self.rates[1], 840, 900, '2015-07-01', False),
            ]
        ]

        self.benefits = [
            self.benefit_model.create({
                'category_id': benefit[0].id,
                'rate_id': benefit[1].id,
                'date_start': benefit[2],
                'date_end': benefit[3],
                'contract_id': self.contract.id,
            })
            for benefit in [
                (self.categories[0], self.rates[0],
                    '2015-01-01', '2015-12-31'),
                (self.categories[1], self.rates[1],
                    '2015-01-01', '2015-12-31'),
            ]
        ]

        self.payslip = self.payslip_model.create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': '2015-01-01',
            'date_to': '2015-01-31',
            'struct_id': self.structure.id,
        })

    def compute_payslip(self):
        self.payslip.compute_sheet()
        self.payslip.refresh()

        return {
            line.code: line.total
            for line in self.payslip.details_by_salary_rule_category
        }


class TestEmployeeBenefit(TestEmployeeBenefitBase):

    def test_compute_payslip(self):
        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 720 / 12)

    def test_overlapping_dates(self):
        self.payslip.write({
            'date_from': '2015-06-16',
            'date_to': '2015-07-15',
        })

        payslip = self.compute_payslip()

        amount_ben_1 = (20 * 15. + 30 * 15.) / 30
        amount_ben_2 = (600 * 15. + 840 * 15.) / (30 * 12)
        amount_rule_1 = amount_ben_1 + amount_ben_2

        self.assertEqual(payslip['RULE_1'], amount_rule_1)

        amount_rule_2 = (720 * 15. + 900 * 15.) / (30 * 12)

        self.assertEqual(payslip['RULE_2'], amount_rule_2)

    def test_compute_payslip_benefits_added_manually(self):
        """ Compute payslip with benefits added manually
        """
        self.payslip.write({
            'benefit_line_ids': [
                (0, 0, {
                    'category_id': self.categories[0].id,
                    'employee_amount': 1000,
                    'employer_amount': 1500,
                }),
                (0, 0, {
                    'category_id': self.categories[1].id,
                    'employee_amount': 1300,
                    'employer_amount': 1800,
                }),
            ]
        })

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12 + 1000 + 1300)
        self.assertEqual(payslip['RULE_2'], 720 / 12 + 1800)

    def test_compute_payslip_benefit_codes(self):
        """ Test sum_benefits with list of benefit codes as
        parameter
        """
        self.rule.write({
            'amount_python_compute': """
payslip.compute_benefits()
result = rule.sum_benefits(payslip, codes='BEN_1')
"""
        })

        self.rule_2.write({
            'amount_python_compute': """
result = rule.sum_benefits(payslip, codes=['BEN_1', 'BEN_2'], employer=True)
"""
        })

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)

    def test_compute_payslip_no_parameter(self):
        """ Test sum_benefits when the salary rule is related to no
        employee benefit
        """
        self.rule.write({
            'employee_benefit_ids': [(5, 0)],
        })

        self.rule_2.write({
            'employee_benefit_ids': [(5, 0)],
        })

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)
