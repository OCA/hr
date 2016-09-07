# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp import models


class TestHrExpense(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestHrExpense, self).setUp(*args, **kwargs)
        self.obj_expense = self.env["hr.expense.expense"]
        self.obj_product = self.env["product.product"]
        self.department = self.env.ref("hr.dep_management")
        self.job = self.env.ref("hr.job_ceo")
        self.categ1 = self.env.ref("product.product_category_6")
        self.categ1_products = self.obj_product.search([
            ("categ_id", "=", self.categ1.id),
            ("hr_expense_ok", "=", True),
        ])
        self.categ1_products.write({"hr_expense_ok": True})
        self.categ2 = self.env.ref("product.product_category_7")
        self.categ2_products = self.obj_product.search([
            ("categ_id", "=", self.categ2.id),
            ("hr_expense_ok", "=", True),
        ])
        self.categ2_products.write({"hr_expense_ok": True})
        self.categ3 = self.env.ref("product.product_category_8")
        self.categ3_products = self.obj_product.search([
            ("categ_id", "=", self.categ3.id),
            ("hr_expense_ok", "=", True),
        ])
        self.categ3_products.write({"hr_expense_ok": True})
        self.categ4 = self.env.ref("product.product_category_8")
        self.categ4_products = self.obj_product.search([
            ("categ_id", "=", self.categ4.id),
            ("hr_expense_ok", "=", True),
        ])
        self.categ4_products.write({"hr_expense_ok": True})
        self.product1 = self.env.ref("hr_expense.car_travel")
        self.product2 = self.env.ref("hr_expense.air_ticket")
        self.product3 = self.env.ref("hr_expense.hotel_rent")
        self.product4 = self.env.ref("product.product_product_4")
        self.employee = self.env.ref("hr.employee")
        self.employee.write({
            "department_id": self.department.id,
            "job_id": self.job.id})
        self.expense_data = {
            "name": "Daily expense",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "employee_id": self.employee.id,
        }
        self.uom1 = self.env.ref("product.product_uom_unit")
        return result

    def test_onchange_required_product(self):
        self.employee.write({"required_expense_product": True})
        expense = self.obj_expense.create(self.expense_data)
        expense.onchange_employee()
        self.assertEqual(
            expense.required_expense_product,
            True)
        self.employee.write({"required_expense_product": False})
        expense.onchange_employee()
        self.assertEqual(
            expense.required_expense_product,
            False)

    def test_employee_only_product_policy(self):
        self.employee.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ1.id])]
        })
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            self.categ1_products.sorted(key=lambda x: x.id))
        self.categ1_products += self.product1
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])]})
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            self.categ1_products.sorted(key=lambda x: x.id))

    def test_employee_department_product_policy(self):
        self.employee.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ1.id])]
        })
        expected_products = self.categ1_products
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])]})
        expected_products += self.product1
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.department.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ2.id])],
        })
        expected_products += self.categ2_products
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.department.write({
            "allowed_expense_product_ids": [(6, 0, [self.product2.id])],
        })
        expected_products += self.product2
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))

    def test_employee_job_product_policy(self):
        self.employee.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ3.id])]
        })
        expected_products = self.categ1_products
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])]})
        expected_products += self.product1
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.job.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ3.id])],
        })
        expected_products += self.categ3_products
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))
        self.department.write({
            "allowed_expense_product_ids": [(6, 0, [self.product3.id])],
        })
        expected_products += self.product3
        self.assertEqual(
            self.employee.all_allowed_expense_product_ids.sorted(
                key=lambda x: x.id),
            expected_products.sorted(key=lambda x: x.id))

    def test_create_expense_1(self):
        self.employee.write({"required_expense_product": True})
        line1 = {
            "name": "tes line",
            "date_value": self.expense_data["date"],
            "unit_amount": 100.00,
            "uom_id": self.uom1.id,
        }
        self.expense_data.update({
            "required_expense_product": True,
            "line_ids": [
                (0, 0, line1)]})
        with self.assertRaises(models.ValidationError):
            self.obj_expense.create(self.expense_data)
        self.expense_data.update({
            "required_expense_product": False})
        self.obj_expense.create(self.expense_data)

    def test_create_expense_2(self):
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])]
        })
        line1 = {
            "name": "tes line",
            "date_value": self.expense_data["date"],
            "unit_amount": 100.00,
            "product_id": self.product2.id,
            "uom_id": self.product2.uom_id.id,
        }
        self.expense_data.update({
            "limit_product_selection": True,
            "line_ids": [
                (0, 0, line1)]})
        with self.assertRaises(models.ValidationError):
            self.obj_expense.create(self.expense_data)

    def test_create_expense_3(self):
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])]
        })
        line1 = {
            "name": "tes line",
            "date_value": self.expense_data["date"],
            "unit_amount": 100.00,
            "product_id": self.product1.id,
            "uom_id": self.product1.uom_id.id,
        }
        self.expense_data.update({
            "line_ids": [
                (0, 0, line1)]})
        self.obj_expense.create(self.expense_data)

    def test_write_expense_1(self):
        self.employee.write({
            "allowed_expense_product_ids": [(6, 0, [self.product1.id])],
            "required_expense_product": True,
        })
        line1 = {
            "name": "tes line",
            "date_value": self.expense_data["date"],
            "unit_amount": 100.00,
            "uom_id": self.uom1.id,
            "product_id": self.product1.id,
        }
        self.expense_data.update({
            "required_expense_product": True,
            "limit_product_selection": True,
            "line_ids": [
                (0, 0, line1)]})
        expense = self.obj_expense.create(self.expense_data)
        line_id = expense.line_ids[0].id
        res = {
            "line_ids": [(1, line_id, {"product_id": False})],
        }
        with self.assertRaises(models.ValidationError):
            expense.write(res)
        res = {
            "line_ids": [(1, line_id, {"product_id": self.product2.id})],
        }
        with self.assertRaises(models.ValidationError):
            expense.write(res)
