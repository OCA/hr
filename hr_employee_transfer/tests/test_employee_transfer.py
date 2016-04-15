# -*- coding: utf-8 -*-
# © 2015 Salton Massally (<smassally@idtlabs.sl>).

from openerp.tests import common
from openerp import fields


class TestEmployeeTransfer(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeTransfer, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.transfer_model = self.env['hr.department.transfer']
        self.job_model = self.env['hr.job']

        # Create an employees
        self.job = self.job_model.create({'name': 'Job 1'})
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
            'date_start': '2010-10-01',
            'employee_id': self.employee.id,
            'wage': 1000,
            'job_id': self.job.id,
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
