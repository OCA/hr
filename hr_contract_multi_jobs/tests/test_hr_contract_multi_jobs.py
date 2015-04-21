# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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

from openerp.tests.common import TransactionCase
from openerp import exceptions

class TestContractMultiJob(TransactionCase):
    def setUp(self):
        super(TestContractMultiJob, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry('res.users')
        self.contract_model = self.registry('hr.contract')
        self.job_model = self.registry('hr.job')
        self.context = self.user_model.context_get(self.cr, self.uid)

        # Create an employee
        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context)

        # Create 2 jobs
        self.job_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 1'}, context=self.context)

        self.job_2_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 2'}, context=self.context)

        # Create a contract
        self.contract_id = self.contract_model.create(
            self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
            }, context=self.context
        )

        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'job_id': self.job_id
            }, context=self.context)

    def tearDown(self):
        self.contract_model.unlink(
            self.cr, self.uid, [self.contract_id], context=self.context)

        self.employee_model.unlink(
            self.cr, self.uid, [self.employee_id], context=self.context)

        self.job_model.unlink(
            self.cr, self.uid,
            [self.job_id, self.job_2_id],
            context=self.context)

        super(TestContractMultiJob, self).tearDown()

    def test_no_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has no assigned job
        and check job_id is False.
        """
        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'contract_job_ids': [],
            }, context=self.context
        )        
        contract = self.contract_model.browse(
            self.cr, self.uid, [self.contract_id], context=self.context
        )
        self.assertFalse(contract.job_id == False)
        
    def test_one_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has one assigned job
        and check is the job_id is set.
        """
        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'is_main_job': True,
                    }),],
            }, context=self.context
        )
        contract = self.contract_model.browse(
            self.cr, self.uid, [self.contract_id], context=self.context
        )
        self.assertTrue(contract.job_id.id == self.job_id)
        
    def test_two_contract_jobs_one_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and check is the job_id is set as main job.
        """
        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'is_main_job': True,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id,
                        'is_main_job': False,
                    }),],
            }, context=self.context
        )
        contract = self.contract_model.browse(
            self.cr, self.uid, [self.contract_id], context=self.context
        )
        self.assertTrue(contract.job_id.id == self.job_id)
        
    def test_two_contract_jobs_two_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and raise error since both are set as main jobs.
        """
        self.assertRaises(
            exceptions.ValidationError, self.contract_model.write,
            self.cr, self.uid, [self.contract_id], {
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'is_main_job': True,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id,
                        'is_main_job': True,
                    }),],
            }, context=self.context
        )
        
