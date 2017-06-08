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
from dateutil.relativedelta import relativedelta
from datetime import date

from openerp.tests import common
from openerp import fields


class TestEndofserviceBenefit(common.TransactionCase):

    def setUp(self):
        super(TestEndofserviceBenefit, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.contract_type_model = self.env['hr.contract.type']
        self.contract_model = self.env['hr.contract']
        self.rule_model = self.env['hr.endofservice.rule']

        # create contrac type
        type = self.contract_type_model.create(
            {
                'name': 'Normal Employee'
            }
        )
        # create terminal rules
        rules = (
            (0, 1, 0),
            (1, 3, 100),
            (3, 10, 200)
        )
        for rule in rules:
            self.rule_model.create(
                {
                    'contract_type_id': type.id,
                    'range_from': rule[0],
                    'range_to': rule[1],
                    'days': rule[2]
                }
            )

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        # create leave type
        self.contract_model.create(
            {
                'name': 'Contract',
                'wage': 5000,
                'type_id': type.id,
                'employee_id': self.employee.id
            }
        )

    def test_terminal_benefit(self):
        self.employee.write({'initial_employment_date': fields.Date.today()})
        self.assertEqual(self.employee.terminal_benefit, 0)

        dt = date.today() - relativedelta(years=1)
        self.employee.write({'initial_employment_date': str(dt)})
        self.assertEqual(self.employee.terminal_benefit, 1 * 5000 * 100)

        dt = date.today() - relativedelta(years=2)
        self.employee.write({'initial_employment_date': str(dt)})
        self.assertEqual(self.employee.terminal_benefit, 2 * 5000 * 100)

        dt = date.today() - relativedelta(years=5)
        self.employee.write({'initial_employment_date': str(dt)})
        self.assertEqual(self.employee.terminal_benefit, 5 * 5000 * 200)
