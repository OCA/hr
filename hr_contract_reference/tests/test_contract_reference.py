# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestContractReference(TransactionCase):
    def setUp(self):
        super(TestContractReference, self).setUp()
        self.employee = self.env["hr.employee"].create({"name": "Emp"})

    def test_contract_reference(self):
        contract = self.env["hr.contract"].create(
            {"employee_id": self.employee.id, "wage": 1000}
        )
        self.assertNotEqual(contract.name, "/")
