# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEmployeeFirstname(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create 3 employees to concatenate the firstname and lastname
        # in name_related
        self.employee1_id = self.env["hr.employee"].create(
            {"firstname": "Jan", "lastname": "Van-Eyck"}
        )
        self.employee2_id = self.env["hr.employee"].create(
            {"firstname": "Jean-Pierre", "lastname": "Carnaud"}
        )
        self.employee3_id = self.env["hr.employee"].create(
            {"firstname": "Famke", "lastname": "Jenssens"}
        )

        # Create 3 employees for split the name_related to
        # firstname and lastname
        self.employee10_id = self.env["hr.employee"].create({"name": " Jan Van-Eyck"})
        self.employee20_id = self.env["hr.employee"].create(
            {"name": "Jean-Pierre Carnaud"}
        )
        self.employee30_id = self.env["hr.employee"].create({"name": "JenssensFamke"})

    def test_get_name(self):
        """
        Validate the _get_name method is concatenating
        the firstname and lastname
        """
        # Check for employee1
        self.assertEqual(self.employee1_id.name, "Jan Van-Eyck")

        # Check for employee2
        self.assertEqual(self.employee2_id.name, "Jean-Pierre Carnaud")

        # Check for employee3
        self.assertEqual(self.employee3_id.name, "Famke Jenssens")

    def test_onchange(self):
        """
        Validate the get_name method is not failing
        """
        field_onchange = self.env["hr.employee"].new({})._onchange_spec()
        self.assertEqual(field_onchange.get("firstname"), "1")
        self.assertEqual(field_onchange.get("lastname"), "1")
        values = {
            "firstname": "Antonio",
            "lastname": "Esposito",
            "name": "test employee",
        }
        for field in self.env["hr.employee"]._fields:
            if field not in values:
                values[field] = False
        # we work on a temporary record
        new_record = self.env["hr.employee"].new(values)

        updates = new_record.onchange(values, ["firstname", "lastname"], field_onchange)
        values.update(updates.get("value", {}))
        self.assertEqual(values["name"], "Antonio Esposito")

    def test_auto_init_name(self):
        """
        Validate the create method if the name is split
        in firstname and lastname
        """
        # Check for employee10
        self.assertEqual(self.employee10_id.firstname, "Jan")
        self.assertEqual(self.employee10_id.lastname, "Van-Eyck")

        # Check for employee20
        self.assertEqual(self.employee20_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee20_id.lastname, "Carnaud")

        # Check for employee30
        self.assertEqual(self.employee30_id.firstname, False)
        self.assertEqual(self.employee30_id.lastname, "JenssensFamke")

    def test_change_name(self):
        self.employee1_id.write({"name": "Jean-Pierre Carnaud-Eyck"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")

    def test_change_name_with_space(self):
        self.employee1_id.write({"name": "  Jean-Pierre  Carnaud-Eyck"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")

    def test_change_firstname(self):
        self.employee1_id.write({"firstname": "Jean-Pierre"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Jean-Pierre Van-Eyck")

    def test_change_lastname(self):
        self.employee1_id.write({"lastname": "Carnaud"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Jan Carnaud")

    def test_change_firstname_and_lastname(self):
        self.employee1_id.write({"firstname": "Jean-Pierre", "lastname": "Carnaud"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Jean-Pierre Carnaud")

    def test_lastname_firstname(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first"
        )

        self.employee1_id.write({"name": "Carnaud-Eyck Jean-Pierre"})
        self.employee1_id.refresh()
        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")

        self.employee1_id.write({"name": "  Carnaud-Eyck  Jean-Pierre"})
        self.employee1_id.refresh()
        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")

        self.employee1_id.write({"firstname": "Jean-Pierre", "lastname": "Carnaud"})
        self.employee1_id.refresh()
        self.assertEqual(self.employee1_id.name, "Carnaud Jean-Pierre")

    @odoo.tests.tagged("-at_install", "post_install")
    def test_update_name_post_install(self):
        empl_demo = self.env.ref("hr.employee_admin")

        self.assertEqual(empl_demo.firstname, "Mitchell")
        self.assertEqual(empl_demo.lastname, "Admin")

    def test_no_name(self):
        self.env["hr.employee"].create({"firstname": "test"})
        self.env["hr.employee"].create({"lastname": "test"})
        self.env["hr.employee"].create({"name": "test"})
        with self.assertRaises(ValidationError):
            self.env["hr.employee"].create({})

    def test_no_firstname_and_lastname(self):
        with self.assertRaises(ValidationError):
            self.employee1_id.write({"firstname": "", "lastname": ""})

    def test_change_firstname_and_lastname_with_set_last_first_comma(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first_comma"
        )
        self.employee1_id.write({"firstname": "Jean-Pierre", "lastname": "Carnaud"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Carnaud, Jean-Pierre")

    def test_change_name_with_space_with_set_last_first_comma(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first_comma"
        )
        self.employee1_id.write({"name": "  Carnaud-Eyck,  Jean-Pierre"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")
