# -*- coding: utf-8 -*-
# © 2016 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestHrPayslip(common.TransactionCase):
    def setUp(self):
        super(TestHrPayslip, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env["res.users"]
        self.payslip_model = self.env["hr.payslip"]
        self.contract_model = self.env["hr.contract"]
        self.rule_model = self.env["hr.salary.rule"]
        self.rule_category_model = self.env["hr.salary.rule.category"]
        self.structure_model = self.env["hr.payroll.structure"]
        self.payslip_line_model = self.env["hr.payslip.line"]

        self.employee = self.employee_model.create({
            'name': 'Employee 1'
        })

        self.employee_2 = self.employee_model.create({
            'name': 'Employee 2'
        })

        self.category = self.rule_category_model.search([])[0]

        self.rule = self.rule_model.create({
            'name': 'Test 1',
            'sequence': 1,
            'code': 'TEST_1',
            'category_id': self.category.id,
            'appears_on_payslip': True,
            'active': True,
            'amount_python_compute': "result = 50",
        })
        self.rule_2 = self.rule_model.create({
            'name': 'Test 2',
            'sequence': 2,
            'code': 'TEST_2',
            'category_id': self.category.id,
            'appears_on_payslip': True,
            'active': True,
            'amount_python_compute': "result = 100",
        })

        # Create a structure
        self.structure = self.structure_model.create({
            'name': 'TEST',
            'parent_id': False,
            'code': 'TEST',
            'rule_ids': [(6, 0, [self.rule.id, self.rule_2.id])]
        })

        # Create contracts
        self.contract = self.contract_model.create({
            'employee_id': self.employee.id,
            'name': 'Contract 1',
            'wage': 50000,
            'struct_id': self.structure.id,
        })

        # Create contracts
        self.contract_2 = self.contract_model.create({
            'employee_id': self.employee_2.id,
            'name': 'Contract 2',
            'wage': 50000,
            'struct_id': self.structure.id,
        })

        self.payslip_ids = {}

        for payslip in [
            # These 3 payslips should be summed over
            (1, '2014-01-01', '2014-01-31', False, self.employee.id,
                self.contract.id),
            (2, '2014-02-01', '2014-02-28', True, self.employee.id,
                self.contract.id),
            (3, '2014-03-01', '2014-03-31', False, self.employee.id,
                self.contract.id),

            # This payslip is the current one
            (4, '2014-04-01', '2014-04-30', False, self.employee.id,
                self.contract.id),

            # These payslips should not be summed over
            # One in 2013 and the other for another employee and the third
            # for a draft payslip
            (5, '2013-12-01', '2013-12-31', False, self.employee.id,
                self.contract.id),
            (6, '2014-01-01', '2014-01-31', False, self.employee_2.id,
                self.contract_2.id),
            (7, '2014-01-01', '2014-01-31', False, self.employee.id,
                self.contract.id),
        ]:
            self.payslip_ids[payslip[0]] = self.payslip_model.create({
                'struct_id': self.structure.id,
                'date_from': payslip[1],
                'date_to': payslip[2],
                'credit_note': payslip[3],
                'employee_id': payslip[4],
                'contract_id': payslip[5],
            }).id

        # Write the lines of payslip
        for line in [
            (self.payslip_ids[1], self.rule.id, 110, 'TEST_1'),
            (self.payslip_ids[1], self.rule_2.id, 120, 'TEST_2'),
            (self.payslip_ids[2], self.rule.id, 130, 'TEST_1'),
            (self.payslip_ids[2], self.rule_2.id, 140, 'TEST_2'),
            (self.payslip_ids[3], self.rule.id, 150, 'TEST_1'),
            (self.payslip_ids[3], self.rule_2.id, 160, 'TEST_2'),

            (self.payslip_ids[5], self.rule.id, 170, 'TEST_1'),
            (self.payslip_ids[5], self.rule_2.id, 180, 'TEST_2'),
            (self.payslip_ids[6], self.rule.id, 190, 'TEST_1'),
            (self.payslip_ids[6], self.rule_2.id, 200, 'TEST_2'),
            (self.payslip_ids[7], self.rule.id, 210, 'TEST_1'),
            (self.payslip_ids[7], self.rule_2.id, 230, 'TEST_2'),
        ]:
            self.payslip_line_model.create({
                'slip_id': line[0],
                'salary_rule_id': line[1],
                'amount': line[2],
                'code': line[3],
                'name': 'Test',
                'category_id': self.category.id,
                'sequence': 1,
            })

        payslips_done = self.payslip_model.browse([
            self.payslip_ids[x] for x in [1, 2, 3, 5, 6]])

        payslips_done.write({'state': 'done'})

    def test_payslip_ytd_amount(self):
        payslip = self.payslip_model.browse(self.payslip_ids[4])
        payslip.compute_sheet()

        payslip.refresh()

        self.assertEqual(len(payslip.line_ids), 2)
        for line in payslip.line_ids:
            if line.code == 'TEST_1':
                self.assertEqual(line.amount_ytd, 50 + 110 + 130 + 150)
            elif line.code == 'TEST_2':
                self.assertEqual(line.amount_ytd, 100 + 120 + 140 + 160)
