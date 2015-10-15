# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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


class test_hr_salary_rule_variable(common.TransactionCase):
    def setUp(self):
        super(test_hr_salary_rule_variable, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.contract_model = self.registry("hr.contract")
        self.variable_model = self.registry("hr.salary.rule.variable")
        self.rule_model = self.registry("hr.salary.rule")
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.structure_model = self.registry("hr.payroll.structure")
        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context
        )

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
                'amount_select': 'code',
                'amount_python_compute': """\
result = payslip.get_rule_variable(rule_id, payslip.date_from)
""",
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
                'amount_select': 'code',
                'amount_python_compute': """\
result = payslip.get_rule_variable(rule_id, payslip.date_from)
""",
            }, context=context
        )

        self.variables = {}
        # Create salary rule variables
        for variable in [
            (1, self.rule_id, '2014-01-01', '2014-01-31',
                'fixed', 500, False),
            (2, self.rule_2_id, '2014-01-01', '2014-01-31',
                'fixed', 75, False),
            # One record for testing with a python dict
            (3, self.rule_id, '2014-02-01', '2014-02-28',
                'python', False, {'TEST': 200}),
            # One record for testing with a python list
            (4, self.rule_2_id, '2014-02-01', '2014-02-28',
                'python', False, [300]),
        ]:
            self.variables[variable[0]] = self.variable_model.create(
                cr, uid, {
                    'salary_rule_id': variable[1],
                    'date_from': variable[2],
                    'date_to': variable[3],
                    'type': variable[4],
                    'fixed_amount': variable[5],
                    'python_code': variable[6],
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
        self.payslip_id = self.payslip_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_id,
                'contract_id': self.contract_id,
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
                'struct_id': self.structure_id,
            }, context=context,
        )

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.unlink(
            cr, uid, [self.payslip_id], context=context)
        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)
        self.rule_model.unlink(
            cr, uid, [self.rule_id, self.rule_2_id], context=context)

        super(test_hr_salary_rule_variable, self).tearDown()

    def test_rule_variable(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        # Check that every payslip lines were tested
        self.assertTrue(len(payslip.line_ids) == 2)

        for line in payslip.line_ids:
            if line.salary_rule_id.id == self.rule_id:
                self.assertTrue(line.total == 500)

            elif line.salary_rule_id.id == self.rule_2_id:
                self.assertTrue(line.total == 75)

            else:
                self.assertTrue(False)

    def test_rule_variable_with_python_code(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.payslip_model.write(
            cr, uid, [self.payslip_id],
            {
                'date_from': '2014-02-01',
                'date_to': '2014-02-28',
            },
            context=context),

        self.rule_model.write(
            cr, uid, [self.rule_id], {
                'amount_python_compute': """\
variable = payslip.get_rule_variable(rule_id, payslip.date_from)
result = variable['TEST']
"""
            }, context=context)

        self.rule_model.write(
            cr, uid, [self.rule_2_id], {
                'amount_python_compute': """\
variable = payslip.get_rule_variable(rule_id, payslip.date_from)
result = variable[0]
"""
            }, context=context)

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        # Check that every payslip lines were tested
        self.assertTrue(len(payslip.line_ids) == 2)

        for line in payslip.line_ids:
            if line.salary_rule_id.id == self.rule_id:
                self.assertTrue(line.total == 200)

            elif line.salary_rule_id.id == self.rule_2_id:
                self.assertTrue(line.total == 300)

            else:
                self.assertTrue(False)
