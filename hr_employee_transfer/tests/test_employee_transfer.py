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


class TestEmployeeTransfer(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeTransfer, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.transfer_model = self.env['hr.department.transfer']
        self.job_model = self.env['hr.job']

        # Create an employees
        self.job_1 = self.job_model.create({'name': 'Job 1'})
        self.job_2 = self.job_model.create({'name': 'Job 2'})
        self.department = self.env['hr.department'].create(
            {'name': 'Department 1'})
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
            'job_id': self.job.id,
            'department_id': self.department.id
        })
        self.contract = self.env["hr.contract"].create({
            'name': 'Contract 1',
            'date_start': fields.Date.to_string(dt),
            'employee_id': self.employee.id,
            'wage': 1000,
            'job_id': self.job_1.id,
        })

        # create transfer
        self.transfer = self.transfer_model.create(
            {
                'employee_id': self.employee.id,
                'src_id': self.job.id,
                'dst_id': self.job_2.id,
                'src_contract_id': self.contract.id,
                'date': fields.Date.today()
            }
        )

        self.transfer.signal_workflow('signal_confirm')
        self.transfer.signal_workflow('signal_pending')

    def test_transfer(self):
        self.assertTrue(self.transfer.dst_contract_id)
        self.assertEqual(self.transfer.src_contract_id)
        self.assertEqual(self.employee.job_id, self.job_2)
