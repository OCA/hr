# Copyright (C) 2025: BizzAppDev Systems Pvt. Ltd.(https://www.bizzappdev.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestHrEmployeeLanguage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.EmployeeLanguage = cls.env["hr.employee.language"]
        cls.employee = cls.Employee.create({"name": "John Doe"})
        cls.languages = cls.EmployeeLanguage.create(
            [
                {
                    "employee_id": cls.employee.id,
                    "name": "en_US",
                    "description": "English",
                },
                {
                    "employee_id": cls.employee.id,
                    "name": "fr_FR",
                    "description": "French",
                },
                {
                    "employee_id": cls.employee.id,
                    "name": "es_ES",
                    "description": "Spanish",
                },
            ]
        )

    def test_employee_has_multiple_languages(self):
        """It should link multiple languages to the employee."""
        # Ensure 3 languages are linked to the employee
        self.assertEqual(len(self.employee.language_ids), 3)
        self.assertSetEqual(
            set(self.employee.language_ids.mapped("name")),
            {"en_US", "fr_FR", "es_ES"},
        )
