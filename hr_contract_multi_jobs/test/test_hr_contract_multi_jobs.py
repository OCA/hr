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

import openerp.tests.common as common

class TestContractMultiJob(common.TransactionCase):
    
    def setUp(self):
        super(TestContractMultiJob, self).setUp()
        self.contract_model = self.registry('hr.contract')
        self.job_model = self.registry('hr.job')
        self.contract_job_model = self.registry('hr.contract.job')
        
    def test_main_job(self)
        """Test computation of job_id in multijobs scenario."""
        contract = self.browse_ref('hr_contract_multi_jobs.'
                                'contract_1')
        self.assertEquals(contract.name, 'Contract 1')
        self.assertEquals(contract.employee_id, 'hr.employee')
        self.assertEquals(contract.wage, 50000)
        
        #Create jobs
        job_1 = self.job_model.browse_ref('hr_contract_multi_jobs.'
                                          'job_1')
        job_2 = self.job_model.browse_ref('hr_contract_multi_jobs.'
                                          'job_2')
        job_3 = self.job_model.browse_ref('hr_contract_multi_jobs.'
                                          'job_3')
        contract._check_one_main_job()
        
        contract_job_1 = self.contract_job_model.create(self.cr, self.uid, {
            'contract_id': contract.id
            'job_id': job_1
            'is_main_job': False)
        
