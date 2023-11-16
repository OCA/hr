# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.tests import TransactionCase


class TestHRPersonalEquipmentRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_personal_equipment_1 = cls.env["product.template"].create(
            {
                "name": "Product Test Personal Equipment 1",
                "is_personal_equipment": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_personal_equipment_2 = cls.env["product.template"].create(
            {
                "name": "Product Test Personal Equipment 2",
                "is_personal_equipment": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
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

        lines = [
            {
                "name": "Personal Equipment 1",
                "product_id": cls.product_personal_equipment_1.product_variant_id.id,
                "quantity": 3,
            },
            {
                "name": "Personal Equipment 2",
                "product_id": cls.product_personal_equipment_2.product_variant_id.id,
                "quantity": 2,
            },
        ]

        cls.personal_equipment_request = (
            cls.env["hr.personal.equipment.request"]
            .with_user(cls.user.id)
            .create(
                {
                    "name": "Personal Equipment Request Test",
                    "employee_id": cls.employee.id,
                    "line_ids": [(0, 0, line) for line in lines],
                }
            )
        )

    def test_request_compute_name(self):
        self.assertTrue(self.personal_equipment_request.name)
        self.assertEqual(
            self.personal_equipment_request.name,
            _("Personal Equipment Request by %s") % "Employee Test",
        )

    def test_request_default_employee(self):
        self.assertTrue(self.personal_equipment_request.employee_id)
        self.assertEqual(
            self.personal_equipment_request.employee_id.id,
            self.employee.id,
        )

    def test_accept_request(self):
        self.assertEqual(self.personal_equipment_request.state, "draft")
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, "draft")
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, "accepted")
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, "accepted")

    def test_cancel_request(self):
        self.assertEqual(self.personal_equipment_request.state, "draft")
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, "draft")
        self.personal_equipment_request.cancel_request()
        self.assertEqual(self.personal_equipment_request.state, "cancelled")
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, "cancelled")

    def test_allocation_compute_name(self):
        self.assertEqual(
            self.personal_equipment_request.line_ids[0].name,
            "Product Test Personal Equipment 1 to Employee Test",
        )

    def test_onchange_uom_id(self):
        self.assertFalse(self.personal_equipment_request.line_ids[0].product_uom_id)
        self.personal_equipment_request.line_ids[0]._onchange_uom_id()
        self.assertTrue(self.personal_equipment_request.line_ids[0].product_uom_id)
        self.assertEqual(
            self.personal_equipment_request.line_ids[0].product_uom_id,
            self.product_personal_equipment_1.uom_id,
        )

    def test_validate_allocation(self):
        self.personal_equipment_request.accept_request()
        allocation = self.personal_equipment_request.line_ids[0]
        self.assertEqual(allocation.state, "accepted")
        allocation.validate_allocation()
        self.assertEqual(allocation.state, "valid")

    def test_expire_allocation(self):
        self.personal_equipment_request.accept_request()
        allocation = self.personal_equipment_request.line_ids[0]
        allocation.validate_allocation()
        self.assertEqual(allocation.state, "valid")
        self.assertFalse(allocation.expiry_date)
        allocation.expire_allocation()
        self.assertEqual(allocation.state, "expired")
        self.assertTrue(allocation.expiry_date)

    def test_action_open_equipment_request(self):
        action = self.employee.action_open_equipment_request()
        self.assertEqual(action["res_model"], "hr.personal.equipment.request")
        self.assertEqual(self.employee.equipment_request_count, 1)

    def test_action_open_personal_equipment(self):
        action = self.employee.action_open_personal_equipment()
        self.assertEqual(action["res_model"], "hr.personal.equipment")
        self.assertEqual(self.employee.personal_equipment_count, 0)
        self.personal_equipment_request.accept_request()
        self.personal_equipment_request.invalidate_recordset()
        self.employee.invalidate_recordset()
        self.assertEqual(self.employee.personal_equipment_count, 2)
