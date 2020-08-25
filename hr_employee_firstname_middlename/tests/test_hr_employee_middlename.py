# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, common

from odoo.addons.hr.tests.common import TestHrCommon


@common.at_install(False)
@common.post_install(True)
class TestEmployeeMiddlename(TestHrCommon):
    def setUp(self):
        super().setUp()
        config = self.env["res.config.settings"].create(
            {"partner_names_order": "first_last"}
        )
        config.execute()
        self.employee_env = self.env["hr.employee"].with_user(self.res_users_hr_officer)

        employee_form = Form(self.employee_env)
        employee_form.firstname = "Jan"
        employee_form.lastname = "Van-Eyck"
        employee_form.middle_name = "Test Middlename"
        self.employee = employee_form.save()

    def test_01_get_name(self):
        self.assertEqual(self.employee.name, "Jan Test Middlename Van-Eyck")

        employee_form = Form(self.employee_env)
        employee_form.firstname = "Jean-Pierre"
        employee_form.lastname = "Carnaud"
        employee_form.middle_name = "Test Middlename"
        employee = employee_form.save()
        self.assertEqual(employee.name, "Jean-Pierre Test Middlename Carnaud")

        employee_form = Form(self.employee_env)
        employee_form.firstname = "Famke"
        employee_form.lastname = "Jenssens"
        employee_form.middle_name = "Test Middlename"
        employee = employee_form.save()
        self.assertEqual(employee.name, "Famke Test Middlename Jenssens")

    def test_02_change_middle_name(self):
        employee_form = Form(self.employee)
        employee_form.middle_name = "Middle"
        self.employee = employee_form.save()
        self.assertEqual(self.employee.name, "Jan Middle Van-Eyck")
        self.assertEqual(self.employee.firstname, "Jan")
        self.assertEqual(self.employee.lastname, "Van-Eyck")
        self.assertEqual(self.employee.middle_name, "Middle")

        employee_form = Form(self.employee)
        employee_form.middle_name = False
        employee = employee_form.save()
        self.assertFalse(employee.middle_name)
        self.assertEqual(self.employee.name, "Jan Van-Eyck")
        self.assertEqual(self.employee.firstname, "Jan")
        self.assertEqual(self.employee.lastname, "Van-Eyck")

    def test_03_change_middle_name_with_space(self):
        employee_form = Form(self.employee)
        employee_form.middle_name = "    Middle"
        self.employee = employee_form.save()
        self.assertEqual(self.employee.name, "Jan Middle Van-Eyck")

    def test_04_change_firstname_and_lastname(self):
        employee_form = Form(self.employee)
        employee_form.firstname = "Jean-Pierre"
        employee_form.lastname = "Carnaud"
        self.employee = employee_form.save()
        self.assertEqual(self.employee.name, "Jean-Pierre Test Middlename Carnaud")

    def test_lastname_firstname(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "partner_names_order", "last_first"
        )
        self.assertEqual(self.employee.name, "Jan Test Middlename Van-Eyck")

        employee_form = Form(self.employee_env)
        employee_form.firstname = "Jean-Pierre"
        employee_form.lastname = "Carnaud"
        employee_form.middle_name = "Test Middlename"
        employee = employee_form.save()
        self.assertEqual(employee.name, "Carnaud Test Middlename Jean-Pierre")

        employee_form = Form(self.employee_env)
        employee_form.firstname = "Famke"
        employee_form.lastname = "Jenssens"
        employee_form.middle_name = "Test Middlename"
        employee = employee_form.save()
        self.assertEqual(employee.name, "Jenssens Test Middlename Famke")

    def test_no_name(self):
        with self.assertRaises(ValidationError):
            self.env["hr.employee"].create({"middlename": "test"})
