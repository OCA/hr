# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime


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

        return result

    def test_force_product(self):
        self.employee.write({"required_expense_product": True})
        expense = self.obj_expense.create(self.expense_data)
        self.assertEqual(
            expense.required_expense_product,
            True)
        self.employee.write({"required_expense_product": False})
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

    def test_expense(self):
        view_expense = self.env.ref("hr_expense.view_expenses_form")
        expense = self.obj_expense.create(self.expense_data)
        expense.fields_view_get(
            view_id=view_expense.id, view_type="form",
            toolbar=False, submenu=False)
        self.employee.write({
            "allowed_expense_product_categ_ids": [(6, 0, [self.categ3.id])]
            })
        expense.fields_view_get(
            view_id=view_expense.id, view_type="form",
            toolbar=False, submenu=False)
