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
        self.exemption_model = self.registry('hr.income.tax.exemption')

        cr, uid, context = self.cr, self.uid, self.context

        self.exemption_id = self.exemption_model.create(cr, uid, {
            'name': 'Test',
        }, context=context)

        self.exemption_2_id = self.exemption_model.create(cr, uid, {
            'name': 'Test',
        }, context=context)

        self.category_model.write(cr, uid, self.category_ids[0], {
            'exemption_ids': [(4, self.exemption_id)]
        }, context=context)

        self.category_model.write(cr, uid, self.category_ids[1], {
            'exemption_ids': [(4, self.exemption_2_id)]
        }, context=context)

    def remove_categories(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.rule_model.write(cr, uid, [self.rule_id, self.rule_2_id], {
            'employee_benefit_ids': [(5, 0)],
        }, context=context)

    def test_rule_with_categories(self):
        """ Test exemptions on rules linked to benefit categories
        No categories are exempted.
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.rule_model.write(cr, uid, [self.rule_id], {
            'exemption_id': self.exemption_id,
        }, context=context)

        self.rule_model.write(cr, uid, [self.rule_2_id], {
            'exemption_id': self.exemption_2_id,
        }, context=context)

        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 720 / 12)

    def test_no_exemption(self):
        self.remove_categories()
        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 20 + 600 / 12)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)

    def test_one_exemption(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.remove_categories()

        self.rule_model.write(cr, uid, [self.rule_id], {
            'exemption_id': self.exemption_id,
        }, context=context)

        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 600 / 12)
        self.assertEqual(payslip['RULE_2'], 40 + 720 / 12)

    def test_two_exemptions(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.remove_categories()

        self.rule_model.write(cr, uid, [self.rule_id], {
            'exemption_id': self.exemption_id,
        }, context=context)

        self.rule_model.write(cr, uid, [self.rule_2_id], {
            'exemption_id': self.exemption_2_id,
        }, context=context)

        payslip = self.compute_payslip()
        self.assertEqual(payslip['RULE_1'], 600 / 12)
        self.assertEqual(payslip['RULE_2'], 40)
