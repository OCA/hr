# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import fields
from odoo.tests import common

from ..hooks import pre_init_hook
from ..models.hr_contract import AMOUNT_PERIOD_SELECTION


class TestHrContractRate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.HrEmployee = cls.env["hr.employee"]
        cls.HrContract = cls.env["hr.contract"]
        cls.employee = cls.HrEmployee.create({"name": "Employee"})

    def _create_contract(self, **vals):
        values = {
            "name": "Contract",
            "employee_id": self.employee.id,
            "date_start": self.today,
            "date_end": self.today,
        }
        values.update(vals)
        return self.HrContract.create(values)

    def _stored(self, contract, *columns):
        contract.flush_recordset()
        self.env.cr.execute(
            # pylint: disable=sql-injection
            f"SELECT {', '.join(columns)} FROM hr_contract WHERE id = %s",
            [contract.id],
        )
        return self.env.cr.fetchone()

    def test_compatibility(self):
        contract = self._create_contract(wage=5000.0)

        self.assertEqual(contract.amount, 5000.0)
        self.assertEqual(contract.amount_period, "month")

    def test_hourly(self):
        contract = self._create_contract(amount=50.0, amount_period="hour")

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_daily(self):
        contract = self._create_contract(amount=400.0, amount_period="day")

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_weekly(self):
        contract = self._create_contract(amount=2000.0, amount_period="week")

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_monthly(self):
        contract = self._create_contract(amount=5000.0, amount_period="month")

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_quarterly(self):
        contract = self._create_contract(amount=15000.0, amount_period="quarter")

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_annual(self):
        contract = self._create_contract(amount=60000.0, amount_period="year")

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_work_units_per_month(self):
        contract = self._create_contract(amount=5000.0)

        self.assertAlmostEqual(contract.work_hours_per_month, 2080.0 / 12.0)
        self.assertAlmostEqual(
            contract.work_days_per_month, contract.work_hours_per_month / 8.0
        )
        self.assertAlmostEqual(
            contract.work_weeks_per_month, contract.work_days_per_month / 5.0
        )

    def test_work_units_drive_the_approximate_wage(self):
        contract = self._create_contract(amount=50.0, amount_period="hour")

        contract.work_hours_per_month = 100.0

        self.assertEqual(contract.approximate_wage, 5000.0)

    def test_change_amount(self):
        contract = self._create_contract(amount=5000.0, amount_period="month")

        contract.amount = 6000.0

        self.assertEqual(contract.wage, 6000.0)

    def test_write_wage(self):
        contract = self._create_contract(amount=50.0, amount_period="hour")

        contract.wage = 2500.0

        self.assertEqual(contract.amount, 2500.0)
        self.assertEqual(contract.amount_period, "month")
        self.assertEqual(contract.wage, 2500.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_write_wage_skip_inverse(self):
        contract = self._create_contract(amount=50.0, amount_period="hour")

        contract.with_context(hr_contract_inverse_wage_skip=True).wage = 999.0

        self.assertEqual(contract.amount, 50.0)
        self.assertEqual(contract.amount_period, "hour")

    def test_amount_period_selection(self):
        field = self.HrContract._fields["amount_period"]

        self.assertEqual(
            [key for key, _label in field._description_selection(self.env)],
            [key for key, _label in AMOUNT_PERIOD_SELECTION],
        )

    def test_form_view(self):
        arch = etree.fromstring(self.HrContract.get_view(view_type="form")["arch"])
        row = arch.find(".//div[@name='wage']")

        self.assertIsNotNone(row)
        self.assertIsNotNone(row.find("field[@name='amount']"))
        self.assertIsNotNone(row.find("field[@name='amount_period']"))
        # Hidden, but still there for the views that extend it.
        self.assertEqual(row.find("field[@name='wage']").get("invisible"), "1")
        self.assertIsNotNone(arch.find(".//label[@for='amount']"))
        self.assertIsNone(arch.find(".//label[@for='wage']"))

    def test_pre_init_hook_seeds_missing_amount(self):
        contract = self._create_contract(wage=5000.0)
        contract.flush_recordset()
        self.env.cr.execute(
            "UPDATE hr_contract SET amount = NULL, amount_period = NULL WHERE id = %s",
            [contract.id],
        )

        pre_init_hook(self.env)

        self.assertEqual(
            self._stored(contract, "amount", "amount_period"), (5000.0, "month")
        )

    def test_pre_init_hook_keeps_existing_amount(self):
        contract = self._create_contract(amount=50.0, amount_period="hour")

        pre_init_hook(self.env)

        self.assertEqual(
            self._stored(contract, "amount", "amount_period"), (50.0, "hour")
        )
