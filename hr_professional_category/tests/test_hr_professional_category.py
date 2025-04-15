# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestHrProfessionalCategory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.employee = cls.env["hr.employee"].create({"name": "Test employee"})
        cls.category = cls.env["hr.professional.category"].create(
            {
                "code": 123,
                "name": "Test category",
            }
        )
        cls.contract = cls.env["hr.contract"].create(
            {
                "name": "Test contract",
                "employee_id": cls.employee.id,
                "resource_calendar_id": cls.calendar.id,
                "date_start": fields.date.today(),
                "professional_category_id": cls.category.id,
                "wage": 1,
            }
        )

    def test_hr_professional_category_name(self):
        self.assertEqual(self.contract.professional_category_id, self.category)
        self.assertEqual(
            self.category.display_name, f"{self.category.code} - {self.category.name}"
        )
