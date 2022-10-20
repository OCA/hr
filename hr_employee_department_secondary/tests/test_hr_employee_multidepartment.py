# Copyright 2021 Som Energia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestHrEmployeeMultidepartment(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.Employee = self.env['hr.employee']

        self.user_test = self.env.ref('base.user_demo')
        self.department = self.env["hr.department"].create({"name": "Department"})
        self.employee1 = self.env['hr.employee'].create({
            'user_id': self.env.uid,
            'name': 'Employee 1',
            'department_id': self.department.id,
            'department_ids': [(6, 0, [self.department.id])]
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
        })
        self.employee3 = self.env['hr.employee'].create({
            'name': 'Employee 3',
        })

    def test_leave__multidepartment_True(self):
        self.employee3.write({
            'department_ids': [(6, 0, [self.department.id])],
            'department_id': self.department.id
        })
        self.assertEqual(
            self.employee1.department_id, self.employee3.department_id)
        self.assertEqual(
            self.employee1.department_ids, self.employee3.department_ids)
        self.assertNotEqual(
            self.employee1.department_ids, self.employee2.department_ids)
        self.assertNotEqual(
            self.employee1.department_id, self.employee2.department_id)
