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


class test_payroll_analysis(common.TransactionCase):
    def get_activity_id(self, job_id):
        job = self.job_model.browse(
            self.cr, self.uid, job_id, context=self.context)
        return job.activity_ids[0].id

    def setUp(self):
        super(test_payroll_analysis, self).setUp()
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.contract_model = self.registry("hr.contract")
        self.rule_model = self.registry("hr.salary.rule")
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.structure_model = self.registry("hr.payroll.structure")
        self.employee_model = self.registry('hr.employee')
        self.analysis_line_model = self.registry('hr.payslip.analysis.line')

        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
            }, context=context)

        # Get any existing category
        self.category_id = self.rule_category_model.search(
            cr, uid, [], context=context)[0]

        # Create salary rules
        self.rule_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 1',
                'sequence': 1,
                'code': 'TEST_1',
                'category_id': self.category_id,
                'appears_on_payslip': True,
                'active': True,
                'amount_select': 'fix',
                'amount_fix': 100,
                'include_in_payroll_analysis': True,
            }, context=context
        )
        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 2',
                'sequence': 2,
                'code': 'TEST_2',
                'category_id': self.category_id,
                'appears_on_payslip': True,
                'active': True,
                'amount_select': 'fix',
                'amount_fix': 200,
                'include_in_payroll_analysis': False,
            }, context=context
        )

        # Create a structure
        self.structure_id = self.structure_model.create(
            cr, uid, {
                'name': 'TEST',
                'parent_id': False,
                'code': 'TEST',
                'rule_ids': [(6, 0, [self.rule_id, self.rule_2_id])]
            }, context=context
        )

        # Create a contract for the employee
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'struct_id': self.structure_id,
            }, context=context
        )

        # Create a payslip
        self.payslip_ids = [
            self.payslip_model.create(
                self.cr, self.uid,
                {
                    'employee_id': self.employee_id,
                    'contract_id': self.contract_id,
                    'date_from': slip[0],
                    'date_to': slip[1],
                    'struct_id': self.structure_id,
                }, context=context)
            for slip in [
                ('2014-01-01', '2014-01-31'),
                ('2014-02-01', '2014-02-28'),
            ]
        ]

        self.payslip_model.compute_sheet(
            cr, uid, self.payslip_ids, context=context)

    def process_sheets(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.process_sheet(
            cr, uid, self.payslip_ids, context=context)

        # Check that the analysis lines were created
        line_ids = self.analysis_line_model.search(
            cr, uid, [('payslip_id', 'in', self.payslip_ids)],
            context=context)

        lines = self.analysis_line_model.browse(
            cr, uid, line_ids, context=context)

        self.assertEqual(len(lines), 2)

        for line in lines:
            self.assertEqual(line.amount, 100)

    def test_payslip_analysis_line_generated(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.process_sheets()

        # Process the payslips a second time
        # Check that there is the same number of analysis lines
        # generated
        self.process_sheets()

        # Cancel a payslip and check that there is only one
        # analysis line left
        self.payslip_model.cancel_sheet(
            cr, uid, [self.payslip_ids[0]], context=context)

        line_ids = self.analysis_line_model.search(
            cr, uid, [('payslip_id', 'in', self.payslip_ids)],
            context=context)

        lines = self.analysis_line_model.browse(
            cr, uid, line_ids, context=context)

        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].payslip_id.id, self.payslip_ids[1])

    def test_salary_rule_refresh(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.process_sheets()

        # Include the second salary rule in the report
        self.rule_model.write(
            cr, uid, [self.rule_2_id],
            {'include_in_payroll_analysis': True}, context=context)

        # Exclude the first salary rule from the report
        self.rule_model.write(
            cr, uid, [self.rule_id],
            {'include_in_payroll_analysis': False}, context=context)

        # Check that the proper lines are now computed
        line_ids = self.analysis_line_model.search(
            cr, uid, [('payslip_id', 'in', self.payslip_ids)],
            context=context)

        lines = self.analysis_line_model.browse(
            cr, uid, line_ids, context=context)

        self.assertEqual(len(lines), 2)

        for line in lines:
            self.assertEqual(line.amount, 200)
