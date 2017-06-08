# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.tests import common


class TestEmployeeContractHistory(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeContractHistory, self).setUp()
        self.contract_model = self.env["hr.contract"]
        self.employee_model = self.env['hr.employee']

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        self.contract_1 = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2012-01-01',
                'date_end': '2012-12-31',
                'wage': 5000
            }
        )
        self.contract_2 = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2013-01-01',
                'wage': 5000
            }
        )

    def test_first_contract(self):
        # test first cotract
        self.assertTrue(
            self.employee.first_contract_id.id == self.contract_1.id)

    def test_current_contract(self):
        # test current cotract
        self.assertTrue(self.employee.contract_id.id == self.contract_2.id)

    def test_add_new_first_contract(self):
        # ad a new contract and see the initia contrat reped
        contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2011-01-01',
                'date_end': '2011-12-31',
                'wage': 5000
            }
        )
        self.assertTrue(
            self.employee.first_contract_id.id == contract.id)

    def test_add_new_current_contract(self):
        # ad a new contract and see the current contract updated
        self.contract_2.write({'date_end': '2013-12-31'})
        contract = self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2014-01-01',
                'date_end': '2016-12-31',
                'wage': 5000
            }
        )
        self.assertTrue(
            self.employee.contract_id.id == contract.id)
