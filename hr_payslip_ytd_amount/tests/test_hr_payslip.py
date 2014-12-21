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


class test_hr_payslip_line_ytd(common.TransactionCase):
    def setUp(self):
        super(test_hr_payslip_line_ytd, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.contract_model = self.registry("hr.contract")
        self.rule_model = self.registry("hr.salary.rule")
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.structure_model = self.registry("hr.payroll.structure")
        self.payslip_line_model = self.registry("hr.payslip.line")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        # Create employees
        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context)

        self.employee_2_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 2'}, context=context)

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
                'amount_fix': 50,
            }, context=context)
        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 2',
                'sequence': 2,
                'code': 'TEST_2',
                'category_id': self.category_id,
                'appears_on_payslip': True,
                'active': True,
                'amount_select': 'fix',
                'amount_fix': 100,
            }, context=context)

        # Create a structure
        self.structure_id = self.structure_model.create(
            cr, uid, {
                'name': 'TEST',
                'parent_id': False,
                'code': 'TEST',
                'rule_ids': [(6, 0, [self.rule_id, self.rule_2_id])]
            }, context=context)

        # Create contracts
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'struct_id': self.structure_id,
            }, context=context)

        # Create contracts
        self.contract_2_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_2_id,
                'name': 'Contract 2',
                'wage': 50000,
                'struct_id': self.structure_id,
            }, context=context)

        # Create payslips
        self.payslip_ids = {
            payslip[0]: self.payslip_model.create(
                self.cr, self.uid, {
                    'struct_id': self.structure_id,
                    'date_from': payslip[1],
                    'date_to': payslip[2],
                    'struct_id': self.structure_id,
                    'credit_note': payslip[3],
                    'employee_id': payslip[4],
                    'contract_id': payslip[5],
                }, context=context)
            for payslip in [
                # These 3 payslips should be summed over
                (1, '2014-01-01', '2014-01-31', False, self.employee_id,
                    self.contract_id),
                (2, '2014-02-01', '2014-02-28', True, self.employee_id,
                    self.contract_id),
                (3, '2014-03-01', '2014-03-31', False, self.employee_id,
                    self.contract_id),

                # This payslip is the current one
                (4, '2014-04-01', '2014-04-30', False, self.employee_id,
                    self.contract_id),

                # These payslips should not be summed over
                # One in 2013 and the other for another employee and the third
                # for a draft payslip
                (5, '2013-12-01', '2013-12-31', False, self.employee_id,
                    self.contract_id),
                (6, '2014-01-01', '2014-01-31', False, self.employee_2_id,
                    self.contract_2_id),
                (7, '2014-01-01', '2014-01-31', False, self.employee_id,
                    self.contract_id),
            ]
        }

        # Write the lines of payslip
        for line in [
            (self.payslip_ids[1], self.rule_id, 110, self.employee_id,
                self.contract_id, 'TEST_1'),
            (self.payslip_ids[1], self.rule_2_id, 120, self.employee_id,
                self.contract_id, 'TEST_2'),
            (self.payslip_ids[2], self.rule_id, 130, self.employee_id,
                self.contract_id, 'TEST_1'),
            (self.payslip_ids[2], self.rule_2_id, 140, self.employee_id,
                self.contract_id, 'TEST_2'),
            (self.payslip_ids[3], self.rule_id, 150, self.employee_id,
                self.contract_id, 'TEST_1'),
            (self.payslip_ids[3], self.rule_2_id, 160, self.employee_id,
                self.contract_id, 'TEST_2'),

            (self.payslip_ids[5], self.rule_id, 170, self.employee_id,
                self.contract_id, 'TEST_1'),
            (self.payslip_ids[5], self.rule_2_id, 180, self.employee_id,
                self.contract_id, 'TEST_2'),
            (self.payslip_ids[6], self.rule_id, 190, self.employee_2_id,
                self.contract_2_id, 'TEST_1'),
            (self.payslip_ids[6], self.rule_2_id, 200, self.employee_2_id,
                self.contract_2_id, 'TEST_2'),
            (self.payslip_ids[7], self.rule_id, 210, self.employee_id,
                self.contract_id, 'TEST_1'),
            (self.payslip_ids[7], self.rule_2_id, 230, self.employee_id,
                self.contract_id, 'TEST_2'),
        ]:
            self.payslip_line_model.create(
                cr, uid, {
                    'slip_id': line[0],
                    'salary_rule_id': line[1],
                    'amount': line[2],
                    'quantity': 1,
                    'rate': 100,
                    'employee_id': line[3],
                    'contract_id': line[4],
                    'code': line[5],
                    'name': 'Test',
                    'category_id': self.category_id,
                }, context=context)

        self.payslip_model.write(
            cr, uid, [self.payslip_ids[x] for x in [1, 2, 3, 5, 6]],
            {'state': 'done'}, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.write(
            cr, uid, self.payslip_ids.values(),
            {'state': 'draft'}, context=context)
        self.payslip_model.unlink(
            cr, uid, self.payslip_ids.values(), context=context)

        self.contract_model.unlink(
            cr, uid, [self.contract_id, self.contract_2_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id, self.employee_2_id], context=context)
        self.rule_model.unlink(
            cr, uid, [self.rule_id, self.rule_2_id], context=context)
        self.structure_model.unlink(
            cr, uid, [self.structure_id], context=context)

        super(test_hr_payslip_line_ytd, self).tearDown()

    def test_payslip_ytd_amount(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_ids[4]], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_ids[4], context=context)

        self.assertEqual(len(payslip.line_ids), 2)
        for line in payslip.line_ids:
            if line.code == 'TEST_1':
                self.assertEqual(line.total_ytd, 50 + 110 - 130 + 150)
            elif line.code == 'TEST_2':
                self.assertEqual(line.total_ytd, 100 + 120 - 140 + 160)
