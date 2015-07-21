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


class test_hr_employee_exemption(common.TransactionCase):
    def setUp(self):
        super(test_hr_employee_exemption, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.exemption_model = self.registry('hr.income.tax.exemption')
        self.rule_model = self.registry('hr.salary.rule')
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.contract_model = self.registry('hr.contract')
        self.structure_model = self.registry("hr.payroll.structure")
        self.payslip_model = self.registry('hr.payslip')
        self.user_model = self.registry("res.users")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.category_id = self.rule_category_model.search(
            cr, uid, [], context=context)[0]

        self.exemption_id = self.exemption_model.create(cr, uid, {
            'name': 'Test',
        }, context=context)

        self.exemption = self.exemption_model.browse(
            cr, uid, self.exemption_id, context=context)

        self.exemption_2_id = self.exemption_model.create(cr, uid, {
            'name': 'Test',
        }, context=context)

        self.exemption_2 = self.exemption_model.browse(
            cr, uid, self.exemption_2_id, context=context)

        self.rule_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 1',
                'sequence': 1,
                'code': 'TEST_1',
                'category_id': self.category_id,
                'amount_select': 'fix',
                'amount_fix': 50,
                'exemption_id': self.exemption_id,
            }, context=context
        )
        self.rule = self.rule_model.browse(
            cr, uid, self.rule_id, context=context)

        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 2',
                'sequence': 2,
                'code': 'TEST_2',
                'category_id': self.category_id,
                'amount_select': 'fix',
                'amount_fix': 75,
                'exemption_id': self.exemption_2_id,
            }, context=context
        )

        self.rule_2 = self.rule_model.browse(
            cr, uid, self.rule_2_id, context=context)

        self.structure_id = self.structure_model.create(
            cr, uid, {
                'name': 'TEST',
                'parent_id': False,
                'code': 'TEST',
                'rule_ids': [(6, 0, [self.rule_id, self.rule_2_id])]
            }, context=context
        )

        self.employee_ids = [
            self.employee_model.create(
                cr, uid, {
                    'name': record[0],
                }, context=context
            ) for record in [
                ('Employee 1', ),
                ('Employee 2', ),
            ]
        ]

        self.employee = self.employee_model.browse(
            cr, uid, self.employee_ids[0], context=context)

        self.contract_ids = [
            self.contract_model.create(self.cr, self.uid, {
                'name': record[0],
                'employee_id': record[1],
                'wage': 50000,
                'struct_id': self.structure_id,
            }, context=self.context)
            for record in [
                ('Contract 1', self.employee_ids[0]),
                ('Contract 2', self.employee_ids[1]),
            ]
        ]

    def compute_payslip(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_id = self.payslip_model.create(cr, uid, {
            'employee_id': self.employee_ids[0],
            'contract_id': self.contract_ids[0],
            'date_from': '2015-01-01',
            'date_to': '2015-01-31',
            'struct_id': self.structure_id,
        }, context=context)

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        return {
            line.code: line.total
            for line in payslip.details_by_salary_rule_category
        }

    def test_no_exemption(self):
        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_one_exemption(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption_id,
            'date_from': '2015-01-01',
            'date_to': '2015-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_two_exemption(self):
        self.employee.write({'exemption_ids': [
            (0, 0, {
                'exemption_id': self.exemption_id,
                'date_from': '2015-01-01',
                'date_to': '2015-12-31',
            }),
            (0, 0, {
                'exemption_id': self.exemption_2_id,
                'date_from': '2015-01-01',
                'date_to': '2015-12-31',
            }),
        ]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 0)

    def test_exemption_no_date_to(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption_id,
            'date_from': '2015-01-01',
            'date_to': False,
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_exemption_date_before(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption_id,
            'date_from': '2014-12-01',
            'date_to': '2014-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_exemption_date_after(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption_id,
            'date_from': '2015-02-01',
            'date_to': '2015-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)
