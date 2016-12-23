# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestHrContractReference(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestHrContractReference, self).setUp(*args, **kwargs)
        # Objects
        self.obj_hr_contract = self.env['hr.contract']
        self.obj_ir_sequence = self.env['ir.sequence']

        # Data Employee
        self.employee = self.env.ref(
            'hr.employee_mit')

        # Data Sequence
        self.sequence = self.env.ref(
            'hr_contract_reference.seq_contract_ref')

    def test_create(self):
        code = self.sequence.get_next_char(
            self.sequence.number_next_actual)
        contract = self.obj_hr_contract.create({
            'employee_id': self.employee.id,
            'wage': 50000,
        })
        self.assertNotEqual(contract.name, '/')
        self.assertEqual(contract.name, code)
