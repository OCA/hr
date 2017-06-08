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


class test_employer_contribution(common.TransactionCase):
    def setUp(self):
        super(test_employer_contribution, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.company_model = self.registry("res.company")
        self.payslip_model = self.registry("hr.payslip")
        self.contribution_model = self.registry("hr.employer.contribution")
        self.contract_model = self.registry("hr.contract")
        self.structure_model = self.registry("hr.payroll.structure")
        self.rule_model = self.registry("hr.salary.rule")
        self.rule_category_model = self.registry("hr.salary.rule.category")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        # Create users
        self.user_ids = {
            user[0]: self.user_model.create(
                cr, uid, {
                    'name': user[1],
                    'login': user[2],
                    'password': 'test',
                }, context=context)
            for user in [
                (1, "User 1", 'test1'),
                (2, "User 2", 'test2'),
                (3, "User 3", 'test3'),
            ]
        }

        # Create companies
        self.company_ids = {
            company[0]: self.company_model.create(
                cr, uid, {
                    'name': company[1],
                }, context=context)
            for company in [
                (1, "Company 1"),
                (2, "Company 2"),
            ]
        }

        # Create employees
        self.employee_ids = {
            employee[0]: self.employee_model.create(
                cr, uid, {
                    'name': employee[1],
                    'user_id': employee[2],
                }, context=context
            ) for employee in [
                (1, 'Employee 1', self.user_ids[1]),
                (2, 'Employee 2', self.user_ids[2]),
                (3, 'Employee 3', self.user_ids[3]),
            ]
        }

        self.category_id = self.rule_category_model.search(
            cr, uid, [('code', '=', 'BASIC')], context=context)[0]

        # create a salary rule
        self.rule_id = self.rule_model.create(
            cr, uid, {
                'name': "Gross for the pay period",
                'sequence': 1,
                'code': "GROSSP",
                'category_id': self.category_id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': ""
                "result = contract.wage / 26",
            }, context=context)

        # Create a payroll structure
        self.structure_id = self.structure_model.create(
            cr, uid, {
                'name': 'Employee Payslip Structure',
                'code': 'TEST_1',
                'rule_ids': [(6, 0, [self.rule_id])],
                'parent_id': False,
            })

        # Create contracts
        self.contract_ids = {
            contract[0]: self.contract_model.create(
                cr, uid, {
                    'name': contract[1],
                    'employee_id': contract[2],
                    'struct_id': self.structure_id,
                    'wage': contract[3],
                    'schedule_pay': 'bi-weekly',
                }, context=context
            ) for contract in [
                (1, 'Contract 1', self.employee_ids[1], 39000),
                (2, 'Contract 2', self.employee_ids[2], 70000),
                (3, 'Contract 3', self.employee_ids[3], 91000),
            ]
        }

        # Create contracts
        self.payslip_ids = {
            payslip[0]: self.payslip_model.create(
                cr, uid, {
                    'contract_id': payslip[1],
                    'employee_id': payslip[2],
                    'struct_id': self.structure_id,
                    'date_from': payslip[3],
                    'date_to': payslip[4],
                    'company_id': payslip[5],
                }, context=context
            ) for payslip in [
                (1, self.contract_ids[1], self.employee_ids[1],
                    '2014-01-01', '2014-01-15', self.company_ids[1]),
                (2, self.contract_ids[1], self.employee_ids[1],
                    '2014-01-16', '2014-01-31', self.company_ids[1]),
                (3, self.contract_ids[1], self.employee_ids[1],
                    '2014-02-01', '2014-02-15', self.company_ids[1]),

                (4, self.contract_ids[2], self.employee_ids[2],
                    '2014-01-01', '2014-01-15', self.company_ids[2]),

                (5, self.contract_ids[3], self.employee_ids[3],
                    '2014-01-01', '2014-01-15', self.company_ids[1]),
                (6, self.contract_ids[3], self.employee_ids[3],
                    '2014-01-16', '2014-01-31', self.company_ids[1]),
            ]
        }

        self.payslip_model.compute_sheet(
            cr, uid, self.payslip_ids.values(), context=context)

        # Confirm each payslips except payslip 6
        self.payslip_model.write(
            cr, uid, self.payslip_ids.values(),
            {'state': 'done'}, context=context)

        self.payslip_model.write(
            cr, uid, [self.payslip_ids[6]],
            {'state': 'draft'}, context=context)

        # Create a salary rule for the contribution
        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': "Contribution line 1",
                'sequence': 1,
                'code': "TEST",
                'category_id': self.category_id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': ""
                "result = payslip.sum(\n"
                "    'GROSSP', '2014-01-01', '2014-01-31',\n"
                "    contribution.company_id.id)\n"
                "result = result * 0.05",
            }, context=context)

        # Create a payroll structure for the contribution
        self.structure_2_id = self.structure_model.create(
            cr, uid, {
                'name': 'Contribution',
                'code': 'TEST',
                'rule_ids': [(6, 0, [self.rule_2_id])],
                'parent_id': False,
            })

        def tearDown(self):
            self.payslip_model.write(
                cr, uid, self.payslip_ids.values(),
                {'state': 'draft'}, context=context)

            self.payslip_model.unlink(
                cr, uid, self.payslip_ids.values(), context=context)

            self.contract_model.unlink(
                cr, uid, self.contract_ids.values(), context=context)

            self.employee_model.unlink(
                cr, uid, self.employee_ids.values(), context=context)

            self.user_model.unlink(
                cr, uid, self.user_ids.values(), context=context)

            self.company_model.unlink(
                cr, uid, self.company_ids.values(), context=context)

            self.structure_model.unlink(
                cr, uid, self.structure_id, context=context)

            self.rule_model.unlink(
                cr, uid, self.rule_id, context=context)

    def test_contribution_sum(self):
        cr, uid, context = self.cr, self.uid, self.context

        # Create a contribution
        contribution_id = self.contribution_model.create(
            cr, uid, {
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
                'struct_id': self.structure_2_id,
                'company_id': self.company_ids[1],
            }, context=context)

        # Compute and approve the contribution
        self.contribution_model.compute_sheet(
            cr, uid, [contribution_id], context=context)

        contribution = self.contribution_model.browse(
            cr, uid, contribution_id, context=context)

        # Only one line should be computed
        self.assertEqual(len(contribution.line_ids), 1)

        # The total of that line must equal
        # (39k + 39k + 91k) * 0.05 / 26 == 325
        # The payslips 1 and 3 are summed
        # Payslip 2 does not match the contribution dates
        # Payslip 4 does not match the contribution company
        # Payslip 5 is draft
        self.assertEqual(contribution.line_ids[0].total, 325)

        self.contribution_model.unlink(
            cr, uid, [contribution_id], context=context)

    def test_contribution_sum_between_range(self):
        cr, uid, context = self.cr, self.uid, self.context

        # Create a contribution
        contribution_id = self.contribution_model.create(
            cr, uid, {
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
                'struct_id': self.structure_2_id,
                'company_id': self.company_ids[1],
            }, context=context)

        # Edit the salary rule
        self.rule_model.write(
            cr, uid, [self.rule_2_id], {
                'amount_python_compute': ""
                "result = payslip.sum_between_range(\n"
                "    'GROSSP', '2014-01-01', '2014-01-31',\n"
                "    1000, 3200, contribution.company_id.id)\n"
            }, context=context)

        # Compute and approve the contribution
        self.contribution_model.compute_sheet(
            cr, uid, [contribution_id], context=context)

        contribution = self.contribution_model.browse(
            cr, uid, contribution_id, context=context)

        # Only one line should be computed
        self.assertEqual(len(contribution.line_ids), 1)

        # The total of that line must equal
        # (39k / 26 + 39k / 26 - 1000) + (3200 - 1000) == 4200
        # The payslips 1 and 3 are summed
        # Payslip 3 does not match the dates
        # Payslip 4 does not match the company
        # Payslip 6 is draft
        self.assertEqual(contribution.line_ids[0].total, 4200)

        self.contribution_model.unlink(
            cr, uid, [contribution_id], context=context)

    def test_contribution_sum_between_range_count(self):
        """test sum_between_range with count_employees is True"""
        cr, uid, context = self.cr, self.uid, self.context

        # Create a contribution
        contribution_id = self.contribution_model.create(
            cr, uid, {
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
                'struct_id': self.structure_2_id,
                'company_id': self.company_ids[1],
            }, context=context)

        # Edit the salary rule
        self.rule_model.write(
            cr, uid, [self.rule_2_id], {
                'amount_python_compute': ""
                "result = payslip.sum_between_range(\n"
                "    'GROSSP', '2014-01-01', '2014-01-31',\n"
                "    1000, 3200, contribution.company_id.id,\n"
                "    count_employees=True)\n"
            }, context=context)

        # Compute and approve the contribution
        self.contribution_model.compute_sheet(
            cr, uid, [contribution_id], context=context)

        contribution = self.contribution_model.browse(
            cr, uid, contribution_id, context=context)

        # Only one line should be computed
        self.assertEqual(len(contribution.line_ids), 1)

        # 2 employees: employee_1 and employee_2
        self.assertEqual(contribution.line_ids[0].total, 2)

        self.contribution_model.unlink(
            cr, uid, [contribution_id], context=context)
