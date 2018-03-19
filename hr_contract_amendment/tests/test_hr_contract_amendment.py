# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class test_contract_amendment(TransactionCase):
    def setUp(self):
        super(test_contract_amendment, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.amendment_model = self.env['hr.contract.amendment']
        self.contract_model = self.env["hr.contract"]
        # Create an employee
        self.employee_id = self.employee_model.create({'name': 'Employee 1'})

        # Create 3 jobs
        # self.job_id = self.job_model.create({'name': 'Job 1'})

        # Create a contract
        self.contract_id = self.contract_model.create(
            {
                'employee_id': self.employee_id.id,
                'name': 'Contract 1',
                'wage': 1000,
            })

    def test_write_contract(self):
        """
        test if amendment create on contract write with new and old vals
        """
        contract = self.contract_id
        contract.write({'wage': 1500, 'name': 'Contract 1Bis'})

        un_amendment = self.env['hr.contract.amendment'].search(
            [('contract_id', '=', self.contract_id.id)])
        self.assertTrue(len(un_amendment) == 1)

        list_changes = self.env['hr.contract.amendment.changes'].search(
            [('amendment_id', '=', un_amendment.id)])
        self.assertTrue(len(list_changes) == 2)
        for change in list_changes:
            if change.value_name == 'wage':
                self.assertTrue(change.value_before == 1000)
                self.assertTrue(change.value_new == 1500)
            elif change.value_name == 'name':
                self.assertTrue(change.value_before == 'Contract 1')
                self.assertTrue(change.value_new == 'Contract 1Bis')
