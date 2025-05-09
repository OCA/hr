# Copyright 2025 Dixmit (http://www.dixmit.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrContractRenew(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "work_location_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.contract = cls.env["hr.contract"].create(
            {
                "name": "Test Contract",
                "state": "open",
                "employee_id": cls.employee.id,
                "date_start": "2025-01-01",
                "wage": 5000,
            }
        )

    def test_renew_contract(self):
        """This test checks that new contract is created with state as draft and today
        date as start date and current contract is set as expired with previous date."""
        wizard = self.env["hr.contract.renew.wizard"].create(
            {
                "contract_id": self.contract.id,
            }
        )
        wizard.action_renew_contract()

        # There must be two contracts (the original and the renewed one).
        self.assertEqual(len(self.employee.contract_ids), 2)

        # The original contract must be set as expired with the previous today's date.
        self.assertEqual(self.contract.state, "close")
        self.assertEqual(
            self.contract.date_end, fields.Date.today() - relativedelta(days=1)
        )

        # The new contract must be in draft state with today as start date.
        new_contract = self.employee.contract_ids.filtered(lambda c: c != self.contract)
        self.assertEqual(new_contract.state, "draft")
        self.assertEqual(new_contract.date_start, fields.Date.today())
