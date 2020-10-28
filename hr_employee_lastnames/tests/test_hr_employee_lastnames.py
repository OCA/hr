from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestEmployeeLastnames(TransactionCase):
    def setUp(self):
        super(TestEmployeeLastnames, self).setUp()
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "first_last"
        )
        self.employee_model = self.env["hr.employee"]

        # Create 3 employees to concatenate the firstname and lastnames
        # in name_related
        self.employee1_id = self.employee_model.create(
            {"firstname": "Manuel", "lastname": "Fernandez", "lastname2": "Gonzalez"}
        )
        self.employee2_id = self.employee_model.create(
            {"firstname": "Jean-Pierre", "lastname": "Carnaud"}
        )
        self.employee3_id = self.employee_model.create(
            {"firstname": "Jenssens", "lastname": "Famke"}
        )

        # Create 3 employees for split the name_related to
        # firstname and lastnames
        self.employee10_id = self.employee_model.create(
            {"name": "Manuel Fernandez Gonzalez"}
        )
        self.employee20_id = self.employee_model.create({"name": "Jean-Pierre Carnaud"})
        self.employee30_id = self.employee_model.create({"name": "JenssensFamke"})

    def test_get_name_lastnames(self):
        """Validate the _get_name_lastnames method is concatenating
        the firstname and lastnames
        """
        # Check for employee1
        self.assertEqual(self.employee1_id.name, "Manuel Fernandez Gonzalez")

        # Check for employee2
        self.assertEqual(self.employee2_id.name, "Jean-Pierre Carnaud")

        # Check for employee3
        self.assertEqual(self.employee3_id.name, "Jenssens Famke")

    def test_onchange(self):
        """Validate the _get_name_lastnames method is not failing"""
        field_onchange = self.employee_model.new({})._onchange_spec()
        self.assertEqual(field_onchange.get("firstname"), "1")
        self.assertEqual(field_onchange.get("lastname"), "1")
        values = {
            "firstname": "Pedro",
            "lastname": "Perez",
            "lastname2": "Hernandez",
            "name": "test employee",
        }
        for field in self.employee_model._fields:
            if field not in values:
                values[field] = False
        # we work on a temporary record
        new_record = self.employee_model.new(values)

        updates = new_record.onchange(
            values, ["firstname", "lastname", "lastname2"], field_onchange
        )
        values.update(updates.get("value", {}))
        self.assertEqual(values["name"], "Pedro Perez Hernandez")

    def test_auto_init_name(self):
        """Validate the create method if the name is split
        in firstname and lastnames
        """
        # Check for employee10
        self.assertEqual(self.employee10_id.firstname, "Manuel")
        self.assertEqual(self.employee10_id.lastname, "Fernandez")
        self.assertEqual(self.employee10_id.lastname2, "Gonzalez")

        # Check for employee20
        self.assertEqual(self.employee20_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee20_id.lastname, "Carnaud")
        self.assertEqual(self.employee20_id.lastname2, False)

        # Check for employee30
        self.assertEqual(self.employee30_id.firstname, False)
        self.assertEqual(self.employee30_id.lastname, "JenssensFamke")
        self.assertEqual(self.employee30_id.lastname2, False)

        employee_without_name = self.employee_model
        with self.assertRaises(exceptions.ValidationError):
            employee_without_name = self.employee_model.create(
                {"firstname": "", "lastname": ""}
            )
        self.assertEqual(employee_without_name, self.employee_model)

    def test_change_name(self):
        self.employee1_id.write({"name": "Pedro Martinez Torres"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Pedro")
        self.assertEqual(self.employee1_id.lastname, "Martinez")
        self.assertEqual(self.employee1_id.lastname2, "Torres")

    def test_change_name_with_space(self):
        self.employee1_id.write({"name": "  Jean-Pierre Carnaud-Eyck"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Jean-Pierre")
        self.assertEqual(self.employee1_id.lastname, "Carnaud-Eyck")
        self.assertEqual(self.employee1_id.lastname2, False)

    def test_change_firstname(self):
        self.employee1_id.write({"firstname": "Pedro"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Pedro Fernandez Gonzalez")

    def test_change_lastname(self):
        self.employee1_id.write({"lastname": "Lopez"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Manuel Lopez Gonzalez")

    def test_change_firstname_and_lastnames(self):
        self.employee1_id.write({"firstname": "Jean-Pierre", "lastname2": "Carnaud"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Jean-Pierre Fernandez Carnaud")

    def test_change_lastname_with_set_last_first(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first"
        )
        self.employee1_id.write({"lastname": "Lopez"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Lopez Gonzalez Manuel")

    def test_change_name_with_set_last_first(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first"
        )
        self.employee1_id.write({"name": "Martinez Torres Pedro"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Pedro")
        self.assertEqual(self.employee1_id.lastname, "Martinez")
        self.assertEqual(self.employee1_id.lastname2, "Torres")

        self.employee1_id.write({"name": ""})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, "Pedro")
        self.assertEqual(self.employee1_id.lastname, "Martinez")
        self.assertEqual(self.employee1_id.lastname2, "Torres")

    def test_change_lastname_with_set_last_first_comma(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "employee_names_order", "last_first_comma"
        )
        self.employee1_id.write({"lastname": "Lopez"})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, "Lopez Gonzalez, Manuel")
