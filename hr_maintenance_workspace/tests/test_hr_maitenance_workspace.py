# Copyright 2022 SDi Digital Group (https://www.sdi.es/odoo-cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestHRMaintenanceWorkspace(TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_test = self.env["hr.employee"].create(
            {
                "name": "Employee Test",
            }
        )
        self.equipment_test = self.env["maintenance.equipment"].create(
            {
                "name": "Equipment Test",
                "employee_id": self.employee_test.id,
            }
        )
        self.workspace_test = self.env["maintenance.workspace"].create(
            {
                "name": "Workspace Test",
                "description": "Description",
                "location": "Office 1",
                "employee_ids": [(6, 0, [self.employee_test.id])],
                "equipment_ids": [(6, 0, [self.equipment_test.id])],
            }
        )

    def test_workspace_compute_employee_count(self):
        self.workspace_test._compute_employee_count()
        self.assertEqual(self.workspace_test.employee_count, 1)

    def test_workspace_compute_equipment_count(self):
        self.workspace_test._compute_equipment_count()
        self.assertEqual(self.workspace_test.equipment_count, 1)

    def test_workspace_compute_employee_equipment_count(self):
        self.workspace_test._compute_employee_equipment_count()
        self.assertEqual(self.workspace_test.employee_equipment_count, 1)
        self.workspace_test.write(
            {
                "employee_ids": False,
            }
        )
        self.assertEqual(self.workspace_test.employee_equipment_count, 0)

    def test_workspace_button_employee_count(self):
        action = self.workspace_test.button_employee_equipment_count()
        self.assertEqual(
            action["domain"], [("employee_id", "in", [self.employee_test.id])]
        )

    def test_employee_workspace_count(self):
        self.employee_test._compute_workspace_count()
        self.assertEqual(self.employee_test.workspace_count, 1)

    def test_employee_button_employee_workspaces(self):
        action = self.employee_test.button_employee_workspaces()
        self.assertEqual(
            action["domain"], [("employee_ids", "=", self.employee_test.id)]
        )

    def test_equipment_assign_to_employee(self):
        self.equipment_test.write(
            {
                "equipment_assign_to": "employee",
            }
        )
        self.equipment_test._compute_equipment_assign()
        self.assertEqual(self.equipment_test.workspace_id.id, False)

    def test_equipment_assign_to_department(self):
        self.equipment_test.write(
            {
                "equipment_assign_to": "department",
            }
        )
        self.equipment_test._compute_equipment_assign()
        self.assertEqual(self.equipment_test.workspace_id.id, False)

    def test_equipment_assign_to_workspace(self):
        self.equipment_test.write(
            {
                "equipment_assign_to": "workspace",
            }
        )
        self.equipment_test._compute_equipment_assign()
        self.assertEqual(
            self.equipment_test.workspace_id, self.equipment_test.workspace_id
        )
        self.assertEqual(self.equipment_test.department_id.id, False)
        self.assertEqual(self.equipment_test.employee_id.id, False)

    def test_equipment_assign_to_other(self):
        self.equipment_test.write(
            {
                "equipment_assign_to": "other",
            }
        )
        self.equipment_test._compute_equipment_assign()
        self.assertEqual(
            self.equipment_test.workspace_id, self.equipment_test.workspace_id
        )
