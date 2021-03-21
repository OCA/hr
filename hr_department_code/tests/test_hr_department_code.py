# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestHrDepartmentCode(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department_model = cls.env["hr.department"]

    def create_department(self, name, code=False):
        return self.department_model.create({"name": name, "code": code})

    def test_name_get_department(self):
        department1 = self.create_department("Department1")
        self.assertEqual(department1.name, "Department1")
        self.assertEqual(department1.name_get()[0][1], "Department1")

    def test_name_search_department(self):
        department2 = self.create_department("Department2", code="D2")
        self.assertEqual(department2.name, "Department2")
        self.assertEqual(department2.code, "D2")
        self.assertEqual(department2.name_get()[0][1], "[D2] Department2")
        check_method1 = department2.name_search(
            name="D2", operator="ilike", args=[("id", "=", department2.id)]
        )
        self.assertEqual(check_method1[0][0], department2.id)
