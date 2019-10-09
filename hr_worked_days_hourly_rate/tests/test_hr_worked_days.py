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


class test_worked_days(common.TransactionCase):
    def setUp(self):
        super(test_worked_days, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.context = self.user_model.context_get(self.cr, self.uid)

        # Create an employee
        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context
        )

        # Create a contract for the employee
        self.contract_id = self.contract_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
            },
            context=self.context
        )

        # Create a payslip
        self.payslip_id = self.payslip_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_id,
                'contract_id': self.contract_id,
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
            },
            context=self.context,
        )

    def tearDown(self):
        self.payslip_model.unlink(
            self.cr, self.uid, [self.payslip_id], context=self.context)
        self.contract_model.unlink(
            self.cr, self.uid, [self.contract_id], context=self.context)
        self.employee_model.unlink(
            self.cr, self.uid, [self.employee_id], context=self.context)
        super(test_worked_days, self).tearDown()

    def test_total(self):
        worked_days_id = self.worked_days_model.create(
            self.cr, self.uid,
            {
                'date_from': '2014-01-01',
                'date_to': '2014-01-05',
                'number_of_hours': 40,
                'hourly_rate': 25,
                'rate': 150,
                'payslip_id': self.payslip_id,
                'code': 'test',
                'name': 'test',
                'contract_id': self.contract_id,
            },
            context=self.context,
        )

        worked_days = self.worked_days_model.browse(
            self.cr, self.uid, worked_days_id, context=self.context)

        self.assertEqual(worked_days.total, 40 * 25 * 1.5)
