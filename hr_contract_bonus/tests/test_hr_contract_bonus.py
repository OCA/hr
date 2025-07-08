# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields
from odoo.tests import common


class TestHRContractBonus(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract_id = cls.env["hr.contract"].create(
            {
                "name": "Test Contract",
                "employee_id": cls.env.ref("hr.employee_admin").id,
                "wage": 2000.0,
                "date_start": fields.Date.today(),
            }
        )
        cls.bonus_id = cls.env["hr.contract.bonus"].create(
            {
                "name": "Test Bonus",
                "amount": 1000.0,
                "type": "fixed",
                "frequency": "yearly",
            }
        )
        cls.contract_id.bonus_ids = [(4, cls.bonus_id.id)]

    def test_total_anual_wage(self):
        self.assertEqual(self.contract_id.total_annual_wage_without_bonus, 24000.0)
        self.assertEqual(self.contract_id.total_annual_wage_with_bonus, 25000.0)
        self.bonus_id.write(
            {
                "amount": 200.0,
                "frequency": "monthly",
            }
        )
        self.assertEqual(self.contract_id.total_annual_wage_with_bonus, 26400.0)
        self.bonus_id.write({"type": "percentage", "amount": 2.0})
        self.assertEqual(self.contract_id.total_annual_wage_with_bonus, 24480.0)
        self.bonus_id.write({"frequency": "yearly", "amount": 20.0})
        self.assertEqual(self.contract_id.total_annual_wage_with_bonus, 28800.0)
