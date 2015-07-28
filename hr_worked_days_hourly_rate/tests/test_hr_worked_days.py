# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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


class TestWorkedDays(common.TransactionCase):
    def setUp(self):
        super(TestWorkedDays, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env["res.users"]
        self.payslip_model = self.env["hr.payslip"]
        self.worked_days_model = self.env["hr.payslip.worked_days"]
        self.contract_model = self.env["hr.contract"]

        # Create an employee
        self.employee_id = self.employee_model.create({'name': 'Employee 1'})

        # Create a contract for the employee
        self.contract_id = self.contract_model.create({
            'employee_id': self.employee_id.id,
            'name': 'Contract 1',
            'wage': 50000,
            })

        # Create a payslip
        self.payslip_id = self.payslip_model.create({
            'employee_id': self.employee_id.id,
            'contract_id': self.contract_id.id,
            'date_from': '2014-01-01',
            'date_to': '2014-01-31',
            })

    def test_total(self):
        worked_days = self.worked_days_model.create({
            'date_from': '2014-01-01',
            'date_to': '2014-01-05',
            'number_of_hours': 40,
            'hourly_rate': 25,
            'rate': 150,
            'payslip_id': self.payslip_id.id,
            'code': 'test',
            'name': 'test',
            'contract_id': self.contract_id.id,
            })

        self.assertEqual(worked_days.total, 40 * 25 * 1.5)
