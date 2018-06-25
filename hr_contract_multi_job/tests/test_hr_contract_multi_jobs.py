# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestContractMultiJob(TransactionCase):
    def setUp(self):
        super(TestContractMultiJob, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env['res.users']
        self.contract_model = self.env['hr.contract']
        self.job_model = self.env['hr.job']

        # Create an employee
        self.employee_id = self.employee_model.create({'name': 'Employee 1'})

        # Create 2 jobs
        self.job_id = self.job_model.create({'name': 'Job 1'})

        self.job_2_id = self.job_model.create({'name': 'Job 2'})

        # Create a contract
        self.contract_id = self.contract_model.create(
            {
                'employee_id': self.employee_id.id,
                'name': 'Contract 1',
                'wage': 50000,
            }
        )

    def test_no_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has no assigned job
        and check job_id is False.
        """
        self.contract_id.write({'contract_job_ids': []})
        self.assertFalse(self.contract_id.job_id is False)

    def test_one_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has one assigned job
        and check is the job_id is set.
        """
        self.contract_id.write({'contract_job_ids':
                                [(0, 0, {'job_id': self.job_id.id,
                                         'is_main_job': True})]})
        self.assertEqual(self.contract_id.job_id.id, self.job_id.id)

    def test_two_contract_jobs_one_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and check is the job_id is set as main job.
        """
        self.contract_id.write({'contract_job_ids':
                                [(0, 0, {'job_id': self.job_id.id,
                                         'is_main_job': True}),
                                 (0, 0, {'job_id': self.job_2_id.id,
                                         'is_main_job': False})]})
        self.assertEqual(self.contract_id.job_id.id, self.job_id.id)

    def test_two_contract_jobs_two_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and raise error since both are set as main jobs.
        """
        self.assertRaises(
            exceptions.ValidationError,
            self.contract_id.write,
            {'contract_job_ids': [(0, 0, {'job_id': self.job_id.id,
                                          'is_main_job': True}),
                                  (0, 0, {'job_id': self.job_2_id.id,
                                          'is_main_job': True})]})
