# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrDepartmentCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department_model = cls.env["hr.department"]

    def create_department(self, name, code=False):
        return self.department_model.create({"name": name, "code": code})

    def test_name_get_department(self):
        department1 = self.create_department("Department1")
        self.assertEqual(department1.name, "Department1")
        self.assertEqual(department1.display_name, "Department1")

        department2 = self.create_department("Department2", code="DPT2")
        self.assertEqual(department2.name, "Department2")
        self.assertEqual(department2.code, "DPT2")
        self.assertEqual(department2.display_name, "[DPT2] Department2")
