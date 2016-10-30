# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError
from openerp.tests.common import TransactionCase
from openerp import tools


class HrContractInputType(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(HrContractInputType, self).setUp(*args, **kwargs)
        self.obj_type = self.env[
            "hr.payslip.input_type"]
        self.obj_contract = self.env[
            "hr.contract"]
        self.obj_contract_input_type = self.env[
            "hr.contract.input_type"]

    @tools.mute_logger("openerp.sql_db")
    def test_no_duplicate(self):

        type1 = self.obj_type.create({
            "code": "X1",
            "name": "Example 1",
        })

        type2 = self.obj_type.create({
            "code": "X2",
            "name": "Example 2",
        })

        contract = self.obj_contract.create({
            "name": "X Contract",
            "employee_id": self.env.ref(
                "hr.employee").id,
            "struct_id": self.env.ref(
                "hr_payroll.structure_001").id,
            "wage": 7000.00,
        })

        self.obj_contract_input_type.create({
            "contract_id": contract.id,
            "input_type_id": type1.id,
            "amount": 777.00,
        })

        self.obj_contract_input_type.create({
            "contract_id": contract.id,
            "input_type_id": type2.id,
            "amount": 999.00,
        })

        with self.assertRaises(IntegrityError):
            self.obj_contract_input_type.create({
                "contract_id": contract.id,
                "input_type_id": type1.id,
                "amount": 888.00,
            })
