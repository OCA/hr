# coding: utf-8
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


class TestHrEmployeeExemption(common.TransactionCase):
    def setUp(self):
        super(TestHrEmployeeExemption, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.exemption_model = self.env['hr.income.tax.exemption']
        self.rule_model = self.env['hr.salary.rule']
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.contract_model = self.env['hr.contract']
        self.structure_model = self.env["hr.payroll.structure"]
        self.payslip_model = self.env['hr.payslip']
        self.user_model = self.env["res.users"]

        self.category = self.rule_category_model.search([], limit=1)

        self.exemption = self.exemption_model.create({
            'name': 'Test',
        })

        self.exemption_2 = self.exemption_model.create({
            'name': 'Test',
        })

        self.rule = self.rule_model.create({
            'name': 'Test 1',
            'sequence': 1,
            'code': 'TEST_1',
            'category_id': self.category.id,
            'amount_select': 'fix',
            'amount_fix': 50,
            'exemption_id': self.exemption.id,
        })

        self.rule_2 = self.rule_model.create({
            'name': 'Test 2',
            'sequence': 2,
            'code': 'TEST_2',
            'category_id': self.category.id,
            'amount_select': 'fix',
            'amount_fix': 75,
            'exemption_id': self.exemption_2.id,
        })

        self.structure = self.structure_model.create({
            'name': 'TEST',
            'parent_id': False,
            'code': 'TEST',
            'rule_ids': [(6, 0, [self.rule.id, self.rule_2.id])]
        })

        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        self.employee_2 = self.employee_model.create({
            'name': 'Employee 2',
        })

        self.contract = self.contract_model.create({
            'name': 'Contract 1',
            'employee_id': self.employee.id,
            'wage': 50000,
            'struct_id': self.structure.id,
        })

        self.contract_2 = self.contract_model.create({
            'name': 'Contract 2',
            'employee_id': self.employee_2.id,
            'wage': 50000,
            'struct_id': self.structure.id,
        })

    def compute_payslip(self):
        self.payslip = self.payslip_model.create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': '2015-01-01',
            'date_to': '2015-01-31',
            'struct_id': self.structure.id,
        })

        self.payslip.compute_sheet()
        self.payslip.refresh()

        return {
            line.code: line.total
            for line in self.payslip.details_by_salary_rule_category
        }

    def test_no_exemption(self):
        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_one_exemption(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption.id,
            'date_from': '2015-01-01',
            'date_to': '2015-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_two_exemption(self):
        self.employee.write({'exemption_ids': [
            (0, 0, {
                'exemption_id': self.exemption.id,
                'date_from': '2015-01-01',
                'date_to': '2015-12-31',
            }),
            (0, 0, {
                'exemption_id': self.exemption_2.id,
                'date_from': '2015-01-01',
                'date_to': '2015-12-31',
            }),
        ]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 0)

    def test_exemption_no_date_to(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption.id,
            'date_from': '2015-01-01',
            'date_to': False,
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 0)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_exemption_date_before(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption.id,
            'date_from': '2014-12-01',
            'date_to': '2014-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)

    def test_exemption_date_after(self):
        self.employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption.id,
            'date_from': '2015-02-01',
            'date_to': '2015-12-31',
        })]})

        payslip = self.compute_payslip()

        self.assertEqual(payslip['TEST_1'], 50)
        self.assertEqual(payslip['TEST_2'], 75)
