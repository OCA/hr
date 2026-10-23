# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from datetime import date, datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_cron import _intervalTypes


class TestHREmployeePPE(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_employee_ppe_expirable = cls.env["product.template"].create(
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
        cls.product_employee_ppe_no_expirable = cls.env["product.template"].create(
            {
                "name": "Product Test Employee No PPE",
                "is_personal_equipment": True,
                "is_ppe": True,
                "indications": "Test indications",
                "expirable_ppe": False,
            }
        )
        cls.user = (
            cls.env["res.users"]
            .sudo()
            .create(
                {
                    "name": "Test User",
                    "login": "user@test.com",
                    "email": "user@test.com",
                    "groups_id": [
                        (4, cls.env.ref("base.group_user").id),
                        (4, cls.env.ref("hr.group_hr_user").id),
                    ],
                }
            )
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Employee Test", "user_id": cls.user.id}
        )
        product_exp = cls.product_employee_ppe_expirable.product_variant_id
        product_no_exp = cls.product_employee_ppe_no_expirable.product_variant_id
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

        cls.personal_equipment_request = (
            cls.env["hr.personal.equipment.request"]
            .with_user(cls.user.id)
            .create(
                {
                    "name": "Personal Equipment Request Test",
                    "line_ids": [(0, 0, line) for line in lines],
                }
            )
        )

        cls.hr_employee_ppe_expirable = cls.personal_equipment_request.line_ids[0]
        cls.hr_employee_ppe_no_expirable = cls.personal_equipment_request.line_ids[1]

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


class TestHREmployeePPECertification(TransactionCase):
    """The certificate of approval belongs to the equipment, the allocation
    records which certificate the worker was actually handed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create(
            {
                "name": "Helmet",
                "is_personal_equipment": True,
                "is_ppe": True,
                "ppe_certification": "CA-12345",
                "ppe_certification_expiry_date": date.today() + timedelta(days=365),
            }
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Worker Test"})

    def _create_request(self, product=None):
        return self.env["hr.personal.equipment.request"].create(
            {
                "employee_id": self.employee.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": (
                                product or self.product
                            ).product_variant_id.id,
                            "quantity": 1,
                        },
                    )
                ],
            }
        )

    def test_certificate_is_copied_on_acceptance(self):
        request = self._create_request()
        allocation = request.line_ids

        self.assertFalse(allocation.certification)
        request.accept_request()

        self.assertEqual(allocation.certification, "CA-12345")
        self.assertEqual(
            allocation.certification_expiry_date,
            self.product.ppe_certification_expiry_date,
        )

    def test_renewing_the_product_certificate_does_not_rewrite_past_deliveries(self):
        """The whole point of freezing: an inspection asks which certificate
        was valid on the delivery date."""
        request = self._create_request()
        allocation = request.line_ids
        request.accept_request()

        self.product.write(
            {
                "ppe_certification": "CA-99999",
                "ppe_certification_expiry_date": date.today() + timedelta(days=730),
            }
        )

        self.assertEqual(allocation.certification, "CA-12345")
        self.assertNotEqual(
            allocation.certification_expiry_date,
            self.product.ppe_certification_expiry_date,
        )

    def test_manually_entered_certificate_is_kept(self):
        request = self._create_request()
        allocation = request.line_ids
        allocation.certification = "CA-MANUAL"

        request.accept_request()

        self.assertEqual(allocation.certification, "CA-MANUAL")

    def test_expired_certificate_blocks_the_delivery(self):
        self.product.ppe_certification_expiry_date = date.today() - timedelta(days=1)
        request = self._create_request()

        with self.assertRaises(ValidationError):
            request.accept_request()

    def test_certificate_without_expiry_date_does_not_block(self):
        self.product.ppe_certification_expiry_date = False
        request = self._create_request()

        request.accept_request()

        self.assertEqual(request.line_ids.certification, "CA-12345")

    def test_non_ppe_product_is_untouched(self):
        plain = self.env["product.template"].create(
            {
                "name": "Laptop",
                "is_personal_equipment": True,
                "is_ppe": False,
                "ppe_certification": "SHOULD-NOT-BE-COPIED",
            }
        )
        request = self._create_request(product=plain)

        request.accept_request()

        self.assertFalse(request.line_ids.certification)

    def test_product_flags_the_expired_certificate(self):
        self.assertFalse(self.product.ppe_certification_expired)

        self.product.ppe_certification_expiry_date = date.today() - timedelta(days=1)

        self.assertTrue(self.product.ppe_certification_expired)
