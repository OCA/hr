# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from datetime import date, datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_cron import _intervalTypes


class TestHREmployeePPE(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_employee_ppe_expirable = self.env["product.template"].create(
            {
                "name": "Product Test Employee PPE",
                "is_personal_equipment": True,
                "is_ppe": True,
                "indications": "Test indications",
                "expirable_ppe": True,
                "ppe_interval_type": "days",
                "ppe_duration": 3,
            }
        )
        self.product_employee_ppe_no_expirable = self.env["product.template"].create(
            {
                "name": "Product Test Employee No PPE",
                "is_personal_equipment": True,
                "is_ppe": True,
                "indications": "Test indications",
                "expirable_ppe": False,
            }
        )
        self.user = (
            self.env["res.users"]
            .sudo()
            .create(
                {
                    "name": "Test User",
                    "login": "user@test.com",
                    "email": "user@test.com",
                    "groups_id": [
                        (4, self.env.ref("base.group_user").id),
                        (4, self.env.ref("hr.group_hr_user").id),
                    ],
                }
            )
        )
        self.employee = self.env["hr.employee"].create(
            {"name": "Employee Test", "user_id": self.user.id}
        )
        product_exp = self.product_employee_ppe_expirable.product_variant_id
        product_no_exp = self.product_employee_ppe_no_expirable.product_variant_id
        lines = [
            {
                "name": "Personal Equipment PPE Expirable",
                "product_id": product_exp.id,
                "quantity": 3,
            },
            {
                "name": "Personal Equipment No Expirable",
                "product_id": product_no_exp.id,
                "quantity": 2,
            },
        ]

        self.personal_equipment_request = (
            self.env["hr.personal.equipment.request"]
            .with_user(self.user.id)
            .create(
                {
                    "name": "Personal Equipment Request Test",
                    "line_ids": [(0, 0, line) for line in lines],
                }
            )
        )

        self.hr_employee_ppe_expirable = self.personal_equipment_request.line_ids[0]
        self.hr_employee_ppe_no_expirable = self.personal_equipment_request.line_ids[1]

    def test_compute_fields(self):
        self.hr_employee_ppe_expirable._compute_fields()
        self.assertTrue(self.hr_employee_ppe_expirable.is_ppe)
        self.assertTrue(self.hr_employee_ppe_expirable.expire_ppe)
        self.assertEqual(
            self.hr_employee_ppe_expirable.indications,
            self.product_employee_ppe_expirable.indications,
        )

    def test_accept_allocation(self):
        self.assertFalse(self.hr_employee_ppe_expirable.issued_by)
        self.personal_equipment_request.with_user(self.user).accept_request()
        self.assertTrue(self.hr_employee_ppe_expirable.issued_by)
        self.assertEqual(self.hr_employee_ppe_expirable.issued_by, self.user)

    def test_validate_allocation_with_start_date(self):
        self.assertFalse(self.hr_employee_ppe_expirable.expiry_date)
        self.hr_employee_ppe_expirable.start_date = "2020-01-01"
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertTrue(self.hr_employee_ppe_expirable.expiry_date)
        self.assertEqual(str(self.hr_employee_ppe_expirable.expiry_date), "2020-01-04")

    def test_validate_allocation_without_start_date(self):
        self.assertFalse(self.hr_employee_ppe_expirable.expiry_date)
        self.assertFalse(self.hr_employee_ppe_expirable.start_date)
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertEqual(
            self.hr_employee_ppe_expirable.expiry_date,
            date.today()
            + _intervalTypes[self.product_employee_ppe_expirable.ppe_interval_type](
                self.product_employee_ppe_expirable.ppe_duration
            ),
        )

    def test_cron_ppe_expiry_verification_expired_product(self):
        self.hr_employee_ppe_expirable.start_date = "2020-01-01"
        self.hr_employee_ppe_expirable.expiry_date = "2020-12-31"
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_expirable.state, "valid")
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertEqual(self.hr_employee_ppe_expirable.state, "expired")

    def test_cron_ppe_expiry_verification_no_expired_product(self):
        self.hr_employee_ppe_expirable.expiry_date = (
            datetime.now() + timedelta(days=1)
        ).strftime("%Y-%m-%d")
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_expirable.state, "valid")
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertNotEqual(self.hr_employee_ppe_expirable.state, "expired")

    def test_cron_ppe_expiry_verification_no_expirable_product(self):
        self.hr_employee_ppe_no_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_no_expirable.state, "valid")
        self.hr_employee_ppe_no_expirable.cron_ppe_expiry_verification()
        self.assertNotEqual(self.hr_employee_ppe_no_expirable.state, "expired")

    def test_check_dates(self):
        with self.assertRaises(ValidationError):
            self.hr_employee_ppe_expirable.start_date = "2020-01-01"
            self.hr_employee_ppe_expirable.expiry_date = "2019-12-31"
            self.hr_employee_ppe_expirable._compute_fields()
            self.hr_employee_ppe_expirable.validate_allocation()

    def test_compute_contains_ppe(self):
        # Without ppes
        product_employee_no_ppe = self.env["product.template"].create(
            {
                "name": "Product Test Employee No PPE",
                "is_personal_equipment": True,
                "is_ppe": False,
            }
        )
        product = product_employee_no_ppe.product_variant_id
        lines = [
            {
                "name": "Personal Equipment PPE Expirable",
                "product_id": product.id,
                "quantity": 3,
            }
        ]

        personal_equipment_request = (
            self.env["hr.personal.equipment.request"]
            .with_user(self.user.id)
            .create(
                {
                    "name": "Personal Equipment Request Test",
                    "line_ids": [(0, 0, line) for line in lines],
                }
            )
        )
        personal_equipment_request._compute_contains_ppe()
        self.assertFalse(personal_equipment_request.contains_ppe)

        # With ppes
        product = self.product_employee_ppe_expirable.product_variant_id
        lines.append(
            {
                "name": "Personal Equipment PPE Expirable",
                "is_ppe": True,
                "product_id": product.id,
                "quantity": 3,
            }
        )
        personal_equipment_request["line_ids"] = [(0, 0, line) for line in lines]
        personal_equipment_request._compute_contains_ppe()
        self.assertTrue(personal_equipment_request.contains_ppe)

    def test_action_view_ppe_report(self):
        self.env.company.external_report_layout_id = self.env.ref(
            "web.external_layout_standard"
        ).id
        action = self.personal_equipment_request.action_view_ppe_report()
        self.assertEqual(action["name"], "Receipt of Personal protection Equipment")
        self.assertEqual(len(action["context"]["active_ids"]), 1)
        self.assertEqual(
            action["context"]["active_ids"][0], self.personal_equipment_request.id
        )
        self.assertEqual(action["report_type"], "qweb-pdf")
