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
from openerp.exceptions import ValidationError, Warning as UserWarning
from openerp import fields


class TestEmploymentTermination(common.TransactionCase):

    def setUp(self):
        super(TestEmploymentTermination, self).setUp()
        self.employee_model = self.env['hr.employee']

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        dt = date.today() - relativedelta(months=6)
        self.contract = self.env["hr.contract"].create({
            'name': 'Contract 1',
            'date_start': fields.Date.to_string(dt),
            'employee_id': self.employee.id,
            'wage': 1000
        })

        # termination
        self.reason = self.env['hr.employee.termination.reason'].create(
            {'name': 'Reason'}
        )
        self.termination = self.env['hr.employee.termination'].create(
            {
                'name': fields.Date.today(),
                'reason_id': self.reason.id,
                'employee_id': self.employee.id,
                'notes': 'Hello World'
            }
        )
        self.termination.state_confirm()

    def test_normal_termination(self):
        self.termination.state_done()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.employee.contract_id.date_end, fields.Date.today())

    def test_infuture_contract_end(self):
        dt = date.today() + relativedelta(months=6)
        self.employee.contract_id.date_end = fields.Date.to_string(dt)
        self.termination.state_done()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.employee.contract_id.date_end, fields.Date.today())

    def test_cron_termination(self):
        self.env['hr.employee.termination'].try_terminating_ended()
        self.assertEqual(self.employee.active, False)
        self.assertEqual(
            self.employee.contract_id.date_end, fields.Date.today())

    def test_infuture_effective_dt(self):
        dt = date.today() + relativedelta(months=6)
        self.termination.name = fields.Date.to_string(dt)
        with self.assertRaises(UserWarning):
            self.termination.state_done()

    def test_termination_exists_wiz(self):
        term = self.employee.end_employment_wizard()
        self.assertEqual(term['res_id'], self.termination.id)
