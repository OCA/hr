# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from uuid import uuid4

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


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

    def _create_lot_ids(self, product, quantity):
        product.tracking = "serial"
        lot_ids = []
        for _qty in range(quantity):
            serial_number = str(uuid4())
            lot_id = self.env["stock.lot"].create(
                {
                    "name": f"Lots for tests {product.name} - {serial_number}",
                    "product_id": product.product_variant_id.id,
                }
            )
            lot_ids += lot_id
        return lot_ids

    def test_compute_qty_delivered(self):
        allocation = self.personal_equipment_request.line_ids[0]
        lot_ids = self._create_lot_ids(
            self.product_personal_equipment_1, allocation.quantity
        )
        self.personal_equipment_request.accept_request()
        move = allocation.move_ids[0]
        move.lot_ids = [lot_id.id for lot_id in lot_ids]
        move.quantity_done = allocation.quantity
        picking = self.personal_equipment_request.picking_ids[0]
        picking._action_done()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)
        self.assertEqual(len(allocation.lot_ids), allocation.qty_delivered)
        self.assertEqual(allocation.lot_ids, allocation.move_ids.lot_ids)
        self.assertEqual(allocation.state, "valid")
        # Return picking
        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=picking.id, active_model="stock.picking"
            )
        )
        return_wizard = return_form.save()
        action = return_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        return_picking.move_line_ids.write({"qty_done": 1})
        return_picking.button_validate()
        self.assertEqual(len(self.personal_equipment_request.picking_ids), 2)
        self.assertEqual(allocation.qty_delivered, 0)
        self.assertNotEqual(allocation.lot_ids, allocation.move_ids.lot_ids)
        self.assertFalse(allocation.lot_ids)
        # Duplicate picking
        duplicate_picking = picking.copy()
        lot_ids = self._create_lot_ids(
            self.product_personal_equipment_1, allocation.quantity
        )
        move = duplicate_picking.move_ids
        move.lot_ids = [lot_id.id for lot_id in lot_ids]
        move.quantity_done = allocation.quantity
        duplicate_picking._action_done()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)
        self.assertEqual(len(allocation.lot_ids), allocation.qty_delivered)
        self.assertEqual(allocation.lot_ids, duplicate_picking.move_ids.lot_ids)
        self.assertEqual(allocation.state, "valid")
        # create scraps
        self.assertEqual(allocation.qty_delivered, 3)
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": allocation.product_id.id,
                "scrap_qty": 1.0,
                "location_id": self.location_employee.id,
                "picking_id": duplicate_picking.id,
                "lot_id": lot_ids[0].id,
            }
        )
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")
        self.assertTrue(duplicate_picking.has_scrap_move)
        self.assertEqual(len(allocation.lot_ids), 2)
        self.assertNotIn(lot_ids[0], allocation.lot_ids)
        self.assertEqual(allocation.qty_delivered, 2)

    def test_compute_qty_delivered_without_lot_ids(self):
        allocation = self.personal_equipment_request.line_ids[0]
        self.personal_equipment_request.accept_request()
        move = allocation.move_ids[0]
        move.quantity_done = allocation.quantity
        picking = self.personal_equipment_request.picking_ids[0]
        picking._action_done()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)
        self.assertFalse(allocation.lot_ids)
        self.assertEqual(allocation.lot_ids, allocation.move_ids.lot_ids)
        self.assertEqual(allocation.state, "valid")
        # Return picking
        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=picking.id, active_model="stock.picking"
            )
        )
        return_wizard = return_form.save()
        action = return_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        return_picking.move_line_ids.write({"qty_done": 3})
        return_picking.button_validate()
        self.assertEqual(len(self.personal_equipment_request.picking_ids), 2)
        self.assertEqual(allocation.qty_delivered, 0)
        self.assertEqual(allocation.lot_ids, allocation.move_ids.lot_ids)
        self.assertFalse(allocation.lot_ids)
        # Duplicate picking
        duplicate_picking = picking.copy()
        move = duplicate_picking.move_ids
        move.quantity_done = allocation.quantity
        duplicate_picking._action_done()
        self.assertEqual(allocation.qty_delivered, allocation.quantity)
        self.assertFalse(allocation.lot_ids)
        self.assertEqual(allocation.lot_ids, duplicate_picking.move_ids.lot_ids)
        self.assertEqual(allocation.state, "valid")
        # create scraps
        self.assertEqual(allocation.qty_delivered, 3)
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": allocation.product_id.id,
                "scrap_qty": 1.0,
                "location_id": self.location_employee.id,
                "picking_id": duplicate_picking.id,
            }
        )
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")
        self.assertFalse(scrap.lot_id)
        self.assertTrue(duplicate_picking.has_scrap_move)
        self.assertFalse(allocation.lot_ids)
        self.assertEqual(allocation.qty_delivered, 2)

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
        self._create_lot_ids(self.product_personal_equipment_1, allocation.quantity)
        self.personal_equipment_request.accept_request()
        self.assertEqual(allocation.state, "accepted")
        picking = self.personal_equipment_request.picking_ids[0]
        picking.action_cancel()
        self.assertEqual(allocation.qty_delivered, 0)
        self.assertFalse(allocation.lot_ids)
        self.assertEqual(allocation.state, "cancelled")

    def test_action_cancel_without_qty_delivered(self):
        allocation = self.personal_equipment_request.line_ids[0]
        lot_ids = self._create_lot_ids(
            self.product_personal_equipment_1, allocation.quantity
        )
        self.personal_equipment_request.accept_request()
        self.assertEqual(allocation.state, "accepted")
        move = allocation.move_ids[0]
        move.lot_ids = [lot_ids[index].id for index in range(allocation.quantity - 1)]
        move.quantity_done = allocation.quantity - 1
        picking = self.personal_equipment_request.picking_ids[0]
        picking._action_done()
        back_order = self.personal_equipment_request.picking_ids[1]
        back_order.action_cancel()
        self.assertEqual(allocation.qty_delivered, allocation.quantity - 1)
        self.assertEqual(len(allocation.lot_ids), allocation.qty_delivered)
        self.assertEqual(allocation.lot_ids, allocation.move_ids.lot_ids)
        self.assertEqual(allocation.state, "valid")

    def test_action_view_pickings(self):
        action = self.personal_equipment_request.action_view_pickings()
        self.assertEqual(action["name"], "Transfers")
