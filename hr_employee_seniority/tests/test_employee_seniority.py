# -*- coding: utf-8 -*-
# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrEmployeeSeniority(common.TransactionCase):

    def setUp(self):
        super(TestHrEmployeeSeniority, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.contract_model = self.env["hr.contract"]
        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

    def test_computation_length_of_service(self):
        self.contract1 = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2000-01-01',
                'date_end': '2000-01-31',
                'wage': 5000.0,
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 1.00)
