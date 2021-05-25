# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from datetime import datetime, timedelta

from odoo.tests import SavepointCase

from odoo.exceptions import ValidationError


class TestHREmployeePPE(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHREmployeePPE, cls).setUpClass()
        cls.hr_employee_ppe = cls.env["hr.employee.ppe"]
        cls.hr_employee_ppe_equipment = cls.env["hr.employee.ppe.equipment"]
        cls.product = cls.env["product.product"]
        cls.product_category = cls.env["product.category"].create({
            "parent_id": cls.env.ref("product.product_category_all").id,
            "name": "PPE Test"
            })
        cls.employee = cls.env["hr.employee"].create({
            "name": "Employee 1"
            })
        cls.product_test = cls.product.create({
            "name": "Product test 1",
            "categ_id": cls.product_category.id,
            "type": "consu"
            })
        cls.hr_employee_ppe_equipment_no_expirable = \
            cls.hr_employee_ppe_equipment.create({
                "product_id": cls.product_test.id,
                "expirable": False,
                "indications": "Test Indications"
                })
        cls.hr_employee_ppe_equipment_expirable = cls.hr_employee_ppe_equipment.create({
            "product_id": cls.product_test.id,
            "expirable": True,
            "indications": "Test Indications"
            })
        cls.hr_employee_ppe_no_expirable = cls.hr_employee_ppe.create({
            "ppe_id": cls.hr_employee_ppe_equipment_no_expirable.id,
            "employee_id": cls.employee.id,
            "expire": False
            })
        cls.hr_employee_ppe_expirable = cls.hr_employee_ppe.create({
            "ppe_id": cls.hr_employee_ppe_equipment_expirable.id,
            "employee_id": cls.employee.id,
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            })

    def test_compute_status(self):
        # Expirable product already expired
        self.hr_employee_ppe_expirable._compute_status()
        self.assertEqual(self.hr_employee_ppe_expirable.status, "expired")

        # Expirable product not expired yet
        self.hr_employee_ppe_expirable.end_date = \
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.hr_employee_ppe_expirable._compute_status()
        self.assertEqual(self.hr_employee_ppe_expirable.status, "valid")

        # No expirable product
        self.hr_employee_ppe_no_expirable._compute_status()
        self.assertEqual(self.hr_employee_ppe_no_expirable.status, "valid")

    def test_cron_ppe_expiry_verification(self):
        # Expirable product already expired
        self.hr_employee_ppe_expirable.status = "valid"
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertEqual(self.hr_employee_ppe_expirable.status, "expired")
        # Expirable product not expired yet
        self.hr_employee_ppe_expirable.end_date = (
            datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertEqual(self.hr_employee_ppe_expirable.status, "valid")

    def test_compute_fields(self):
        self.assertEqual(self.hr_employee_ppe_no_expirable.name,
                         "Product test 1 to Employee 1")
        self.assertEqual(self.hr_employee_ppe_no_expirable.expire,
                         self.hr_employee_ppe_equipment_no_expirable.expirable)
        self.assertEqual(self.hr_employee_ppe_no_expirable.indications,
                         self.hr_employee_ppe_equipment_no_expirable.indications)

    def test_check_dates(self):
        with self.assertRaises(ValidationError):
            self.hr_employee_ppe.create({
                "ppe_id": self.hr_employee_ppe_equipment_expirable.id,
                "employee_id": self.employee.id,
                "expire": True
            })
        with self.assertRaises(ValidationError):
            self.hr_employee_ppe.create({
                "ppe_id": self.hr_employee_ppe_equipment_expirable.id,
                "employee_id": self.employee.id,
                "expire": True,
                "start_date": "2020-01-01",
                "end_date": "2019-12-31",
            })
