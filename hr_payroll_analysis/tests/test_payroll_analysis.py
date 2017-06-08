# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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


class TestPayrollAnalysis(common.TransactionCase):
    def get_activity_id(self, job_id):
        job = self.job_model.browse(job_id)
        return job.activity_ids[0].id

    def setUp(self):
        super(TestPayrollAnalysis, self).setUp()
        self.user_model = self.env["res.users"]
        self.payslip_model = self.env["hr.payslip"]
        self.contract_model = self.env["hr.contract"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]
        self.employee_model = self.env['hr.employee']
        self.analysis_line_model = self.env['hr.payslip.analysis.line']

        # Create an employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        # Get any existing category
        self.category = self.rule_category_model.search([])[0]

        # Create salary rules
        self.rule = self.rule_model.create(
            {
                'name': 'Test 1',
                'sequence': 1,
                'code': 'TEST_1',
                'category_id': self.category.id,
                'appears_on_payslip': True,
                'active': True,
                'amount_select': 'fix',
                'amount_fix': 100,
                'include_in_payroll_analysis': True,
            }
        )
        self.rule_2 = self.rule_model.create(
            {
                'name': 'Test 2',
                'sequence': 2,
                'code': 'TEST_2',
                'category_id': self.category.id,
                'appears_on_payslip': True,
                'active': True,
                'amount_select': 'fix',
                'amount_fix': 200,
                'include_in_payroll_analysis': False,
            }
        )

        # Create a structure
        self.structure = self.structure_model.create(
            {
                'name': 'TEST',
                'parent_id': False,
                'code': 'TEST',
                'rule_ids': [(6, 0, [self.rule.id, self.rule_2.id])]
            }
        )

        # Create a contract for the employee
        self.contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'wage': 50000,
                'struct_id': self.structure.id,
            }
        )

        # Create a payslip
        slips = [
            self.payslip_model.create(
                {
                    'employee_id': self.employee.id,
                    'contract_id': self.contract.id,
                    'date_from': slip[0],
                    'date_to': slip[1],
                    'struct_id': self.structure.id,
                })
            for slip in [
                ('2014-01-01', '2014-01-31'),
                ('2014-02-01', '2014-02-28'),
            ]
        ]
        slip_ids = [slip.id for slip in slips]
        self.payslips = self.payslip_model.browse(slip_ids)
        self.payslips.compute_sheet()

    def process_sheets(self):
        self.payslips.process_sheet()

        # Check that the analysis lines were created
        lines = self.analysis_line_model.search(
            [('payslip_id', 'in', self.payslips.ids)],
            )

        self.assertEqual(len(lines), 2)

        for line in lines:
            self.assertEqual(line.amount, 100)

    def test_payslip_analysis_line_generated(self):
        self.process_sheets()

        # Process the payslips a second time
        # Check that there is the same number of analysis lines
        # generated
        self.process_sheets()

        # Cancel a payslip and check that there is only one
        # analysis line left
        self.payslips[0].cancel_sheet()

        lines = self.analysis_line_model.search(
            [('payslip_id', 'in', self.payslips.ids)])

        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].payslip_id.id, self.payslips.ids[1])

    def test_salary_rule_refresh(self):
        self.process_sheets()

        # Include the second salary rule in the report
        self.rule_2.write({'include_in_payroll_analysis': True})

        # Exclude the first salary rule from the report
        self.rule.write({'include_in_payroll_analysis': False})

        # Check that the proper lines are now computed
        lines = self.analysis_line_model.search(
            [('payslip_id', 'in', self.payslips.ids)])

        self.assertEqual(len(lines), 2)

        for line in lines:
            self.assertEqual(line.amount, 200)
