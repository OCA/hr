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
    """ This model must not contain any test, only the setUp method, so that
    it can be inherited.
    """
    def setUp(self):
        super(TestEmployeeBenefitBase, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.contract_model = self.registry("hr.contract")
        self.category_model = self.registry("hr.employee.benefit.category")
        self.benefit_model = self.registry("hr.employee.benefit")
        self.rate_model = self.registry("hr.employee.benefit.rate")
        self.rate_line_model = self.registry("hr.employee.benefit.rate.line")
        self.payslip_model = self.registry("hr.payslip")
        self.rule_model = self.registry("hr.salary.rule")
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.structure_model = self.registry("hr.payroll.structure")
        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        self.category_id = self.rule_category_model.search(
            cr, uid, [], context=context)[0]

        self.rule_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 1',
                'sequence': 1,
                'code': 'RULE_1',
                'category_id': self.category_id,
                'amount_select': 'code',
                'amount_python_compute': """
payslip.compute_benefits()
result = rule.sum_benefits(payslip)
"""
            }, context=context)

        self.rule = self.rule_model.browse(
            cr, uid, self.rule_id, context=context)

        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 2',
                'sequence': 2,
                'code': 'RULE_2',
                'category_id': self.category_id,
                'amount_select': 'code',
                'amount_python_compute': """
result = rule.sum_benefits(payslip, employer=True)
"""
            }, context=context)

        self.rule_2 = self.rule_model.browse(
            cr, uid, self.rule_2_id, context=context)

        self.structure_id = self.structure_model.create(cr, uid, {
            'name': 'TEST',
            'parent_id': False,
            'code': 'TEST',
            'rule_ids': [(6, 0, [self.rule_id, self.rule_2_id])]
        }, context=context)

        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context)

        self.contract_id = self.contract_model.create(self.cr, self.uid, {
            'employee_id': self.employee_id,
            'name': 'Contract 1',
            'wage': 50000,
            'struct_id': self.structure_id,
        }, context=self.context)

        self.category_ids = [
            self.category_model.create(cr, uid, {
                'name': category[0],
                'description': 'Test',
                'code': category[1],
                'salary_rule_ids': [(6, 0, category[2])],
            }, context=context)
            for category in [
                ('Category 1', 'BEN_1', [self.rule_id]),
                ('Category 2', 'BEN_2', [self.rule_id, self.rule_2_id]),
            ]
        ]

        self.rate_ids = [
            self.rate_model.create(cr, uid, {
                'name': 'Test',
                'category_id': rate[0],
                'amount_type': rate[1],
            }, context=context)
            for rate in [
                (self.category_ids[0], 'each_pay'),
                (self.category_ids[1], 'annual'),
            ]
        ]

        self.rate_line_ids = [
            self.rate_line_model.create(cr, uid, {
                'parent_id': line[0],
                'employee_amount': line[1],
                'employer_amount': line[2],
                'date_start': line[3],
                'date_end': line[4],
            }, context=context)
            for line in [
                (self.rate_ids[0], 20, 40, '2015-01-01', '2015-06-30'),
                (self.rate_ids[0], 30, 50, '2015-07-01', False),

                (self.rate_ids[1], 600, 720, '2015-01-01', '2015-06-30'),
                (self.rate_ids[1], 840, 900, '2015-07-01', False),
            ]
        ]

        self.benefit_ids = [
            self.benefit_model.create(cr, uid, {
                'category_id': benefit[0],
                'rate_id': benefit[1],
                'date_start': benefit[2],
                'date_end': benefit[3],
                'contract_id': self.contract_id,
            }, context=context)
            for benefit in [
                (self.category_ids[0], self.rate_ids[0],
                    '2015-01-01', '2015-12-31'),
                (self.category_ids[1], self.rate_ids[1],
                    '2015-01-01', '2015-12-31'),
            ]
        ]

        self.payslip_id = self.payslip_model.create(cr, uid, {
            'employee_id': self.employee_id,
            'contract_id': self.contract_id,
            'date_from': '2015-01-01',
            'date_to': '2015-01-31',
            'struct_id': self.structure_id,
        }, context=context)

    def compute_payslip(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        return {
            line.code: line.total
            for line in payslip.details_by_salary_rule_category
        }


class TestEmployeeBenefit(TestEmployeeBenefitBase):

    def test_compute_payslip(self):
        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 720 / 12)

    def test_overlapping_dates(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.payslip_model.write(cr, uid, [self.payslip_id], {
            'date_from': '2015-06-16',
            'date_to': '2015-07-15',
        }, context=context)

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
        cr, uid, context = self.cr, self.uid, self.context
        self.payslip_model.write(cr, uid, [self.payslip_id], {
            'benefit_line_ids': [
                (0, 0, {
                    'category_id': self.category_ids[0],
                    'employee_amount': 1000,
                    'employer_amount': 1500,
                }),
                (0, 0, {
                    'category_id': self.category_ids[1],
                    'employee_amount': 1300,
                    'employer_amount': 1800,
                }),
            ]
        }, context=context)

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12 + 1000 + 1300)
        self.assertEqual(payslip['RULE_2'], 720 / 12 + 1800)

    def test_compute_payslip_benefit_codes(self):
        """ Test sum_benefits with list of benefit codes as
        parameter
        """
        cr, uid, context = self.cr, self.uid, self.context
        self.rule_model.write(cr, uid, [self.rule_id], {
            'amount_python_compute': """
payslip.compute_benefits()
result = rule.sum_benefits(payslip, codes='BEN_1')
"""
        }, context=context)

        self.rule_model.write(cr, uid, [self.rule_2_id], {
            'amount_python_compute': """
result = rule.sum_benefits(payslip, codes=['BEN_1', 'BEN_2'], employer=True)
"""
        }, context=context)

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)

    def test_compute_payslip_no_parameter(self):
        """ Test sum_benefits when the salary rule is related to no
        employee benefit
        """
        cr, uid, context = self.cr, self.uid, self.context
        self.rule_model.write(cr, uid, [self.rule_id], {
            'employee_benefit_ids': [(5, 0)],
        }, context=context)

        self.rule_model.write(cr, uid, [self.rule_2_id], {
            'employee_benefit_ids': [(5, 0)],
        }, context=context)

        payslip = self.compute_payslip()

        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)
