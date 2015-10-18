# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Salton Massally. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


class TestPayrollAllowance(common.TransactionCase):

    def setUp(self):
        super(TestPayrollAllowance, self).setUp()
        self.payslip_model = self.env["hr.payslip"]
        self.contract_model = self.env["hr.contract"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]
        self.employee_model = self.env['hr.employee']
        self.allowance_model = self.env['hr.payroll.allowance']
        self.allowance_line_model = self.env['hr.payroll.allowance.line']
        self.field_model = self.env['ir.model.fields']

        # Create an employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
            'initial_employment_date': '2014-01-01'
        })

        # Get structure
        self.structure = self.structure_model.search(
            [('code', '=', 'BASE')])[0]

        # Create allowances
        allowances = []
        allowances.append(self.allowance_model.create(
            {
                'name': 'Each Pay',
                'code': 'EACH',
                'struct_id': self.structure.id,
            }
        ))
        allowances.append(self.allowance_model.create(
            {
                'name': 'On Anniversary',
                'code': 'ANNIE',
                'struct_id': self.structure.id,
                'interval': 'yearly',
                'yearly_payment_strategy': 'anniversary',
            }
        ))
        allowances.append(self.allowance_model.create(
            {
                'name': 'Start of Year',
                'code': 'START',
                'struct_id': self.structure.id,
                'interval': 'yearly',
                'yearly_payment_strategy': 'yearly',
            }
        ))
        allowances.append(self.allowance_model.create(
            {
                'name': 'Start of Year - Prorate',
                'code': 'STARTPRO',
                'struct_id': self.structure.id,
                'interval': 'yearly',
                'yearly_payment_strategy': 'yearly',
                'yearly_payment_prorate': True,
            }
        ))

        # Create a contract for the employee
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'wage': 50000,
                'struct_id': self.structure.id,
                'date_start': '2014-01-01'
            }
        )

        # let's create allowances
        [
            self.allowance_line_model.create(
                {
                    'allowance_id': allowance.id,
                    'contract_id': self.contract.id,
                    'amount': 50000,
                }
            )
            for allowance in allowances
        ]

    def test_allowance_creation_rule_in_struct(self):
        # tests that the created rule for the allowance is added to the
        # salary structure specified
        self.assertTrue('EACH' in self.structure.rule_ids.mapped('code'))

    def test_payslip_computation_each(self):
        # checks that allowance is paid with each pay
        slip = self.payslip_model.create(
            {
                'employee_id': self.employee.id,
                'contract_id': self.contract.id,
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
                'struct_id': self.structure.id,
            }
        )
        slip.compute_sheet()
        line = slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'EACH')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, 50000)  # asset that the correct amount

    def test_payslip_computation_anniversary(self):
        # checks that allowance is paid at each anniversary
        slip = self.payslip_model.create(
            {
                'employee_id': self.employee.id,
                'contract_id': self.contract.id,
                'date_from': '2015-01-01',
                'date_to': '2015-01-31',
                'struct_id': self.structure.id,
            }
        )
        slip.compute_sheet()
        line = slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'ANNIE')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, 50000 * 12)  # correct amount

    def test_payslip_computation_start_of_year(self):
        # checks that allowance is paid at the start of the year
        slip = self.payslip_model.create(
            {
                'employee_id': self.employee.id,
                'contract_id': self.contract.id,
                'date_from': '2015-01-01',
                'date_to': '2015-01-31',
                'struct_id': self.structure.id,
            }
        )
        slip.compute_sheet()
        line = slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'START')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, 50000 * 12)  # correct amount

    def test_payslip_computation_prorate(self):
        # checks that allowance is prorated for employee
        self.employee.write({
            'initial_employment_date': '2013-10-01'
        })
        slip = self.payslip_model.create(
            {
                'employee_id': self.employee.id,
                'contract_id': self.contract.id,
                'date_from': '2013-10-01',
                'date_to': '2013-10-31',
                'struct_id': self.structure.id,
            }
        )
        slip.compute_sheet()
        line = slip.line_ids.filtered(
            lambda r: r.salary_rule_id.code == 'STARTPRO')
        self.assertEqual(len(line), 1)  # asset that the line is present
        self.assertEqual(line.total, 50000 * 3)  # correct amount
