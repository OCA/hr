# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestHRPersonalEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.company = cls.env.ref("base.main_company")
        cls.ressuply_loc = cls.env["stock.location"].create(
            {
                "name": "Warehouse Test",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.location_employee = cls.env["stock.location"].create(
            {
                "name": "Employee Personal Equipment Virtual Location",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "transit",
                "is_personal_equipment_location": True,
            }
        )
        cls.route = cls.env["stock.route"].create(
            {
                "name": "Employee Personal Equipment Route",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.company.id,
                "sequence": 10,
            }
        )
        cls.env["stock.rule"].create(
            {
                "name": "Employee Personal Equipment Rule",
                "route_id": cls.route.id,
                "location_src_id": cls.ressuply_loc.id,
                "location_dest_id": cls.location_employee.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.company.id,
                "propagate_cancel": False,
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
                        (4, cls.env.ref("stock.group_stock_manager").id),
                    ],
                }
            )
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Employee Test", "user_id": cls.user.id}
        )
        cls.product_personal_equipment_1 = cls.env["product.template"].create(
            {
                "name": "Product Test Personal Equipment",
                "is_personal_equipment": True,
                "route_ids": [(6, 0, cls.route.ids)],
                "qty_available": 100,
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_personal_equipment_2 = cls.env["product.template"].create(
            {
                "name": "Service Test Personal Equipment 2",
                "is_personal_equipment": True,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        lines = [
            {
                "name": "Personal Equipment 1",
                "product_id": cls.product_personal_equipment_1.product_variant_id.id,
                "quantity": 3,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            },
            {
                "name": "Personal Equipment 2",
                "product_id": cls.product_personal_equipment_2.product_variant_id.id,
                "quantity": 2,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            },
        ]

        cls.personal_equipment_request = (
            cls.env["hr.personal.equipment.request"]
            .with_user(cls.user.id)
            .create(
                {
                    "name": "Personal Equipment Request Test",
                    "line_ids": [(0, 0, line) for line in lines],
                    "location_id": cls.location_employee.id,
                }
            )
        )

    # hr.personal.equipment.request

    def test_get_procurement_group_without_group_set(self):
        self.assertEqual(self.personal_equipment_request.state, "draft")
        self.assertFalse(self.personal_equipment_request.procurement_group_id)
        self.assertFalse(
            self.personal_equipment_request.line_ids[0].procurement_group_id
        )
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, "accepted")
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(
            self.personal_equipment_request.line_ids[0].procurement_group_id
        )

    def test_get_procurement_group_with_group_set(self):
        self.assertEqual(self.personal_equipment_request.state, "draft")
        procurement_group_id = self.env["procurement.group"].create(
            {"move_type": "direct"}
        )
        self.personal_equipment_request.procurement_group_id = procurement_group_id.id
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(
            self.personal_equipment_request.line_ids[0].procurement_group_id
        )
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, "accepted")
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(
            self.personal_equipment_request.line_ids[0].procurement_group_id
        )
        self.assertEqual(
            self.personal_equipment_request.procurement_group_id.id,
            procurement_group_id.id,
        )

    def test_compute_picking_count(self):
        self.assertEqual(self.personal_equipment_request.picking_count, 0)
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.picking_count, 1)

    # hr.personal.equipment

    def test_skip_procurement(self):
        self.personal_equipment_request.line_ids[0]._compute_skip_procurement()
        self.assertFalse(self.personal_equipment_request.line_ids[0].skip_procurement)
        self.personal_equipment_request.line_ids[1]._compute_skip_procurement()
        self.assertTrue(self.personal_equipment_request.line_ids[1].skip_procurement)

    def test_compute_qty_delivered(self):
        self.personal_equipment_request.accept_request()
        allocation = self.personal_equipment_request.line_ids[0]
        move = allocation.move_ids[0]
        move.quantity_done = allocation.quantity
        picking = self.personal_equipment_request.picking_ids[0]
        picking._action_done()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)
        self.assertEqual(allocation.state, "valid")

    def test_quantity_delivered_skip_procurement(self):
        allocation = self.personal_equipment_request.line_ids[1]
        self.personal_equipment_request.accept_request()
        allocation.validate_allocation()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)

    def test_action_launch_procurement_rule_raise_error(self):
        allocation = self.personal_equipment_request.line_ids[0]
        allocation.location_id = None
        with self.assertRaises(UserError):
            self.personal_equipment_request.accept_request()

    # stock.move

    def test_action_cancel_with_qty_delivered(self):
        allocation = self.personal_equipment_request.line_ids[0]
        self.personal_equipment_request.accept_request()
        self.assertEqual(allocation.state, "accepted")
        picking = self.personal_equipment_request.picking_ids[0]
        picking.action_cancel()
        self.assertEqual(allocation.qty_delivered, 0)
        self.assertEqual(allocation.state, "cancelled")

    def test_action_cancel_without_qty_delivered(self):
        allocation = self.personal_equipment_request.line_ids[0]
        self.personal_equipment_request.accept_request()
        self.assertEqual(allocation.state, "accepted")
        move = allocation.move_ids[0]
        move.quantity_done = allocation.quantity - 1
        picking = self.personal_equipment_request.picking_ids[0]
        picking._action_done()
        back_order = self.personal_equipment_request.picking_ids[1]
        back_order.action_cancel()
        self.assertEqual(allocation.qty_delivered, allocation.quantity - 1)
        self.assertEqual(allocation.state, "valid")

    def test_action_view_pickings(self):
        action = self.personal_equipment_request.action_view_pickings()
        self.assertEqual(action["name"], "Transfers")
