# Copyright 2021 Som Energia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestHrEmployeeDepartmentSecondary(common.TransactionCase):

    def setUp(self):
        super(TestHrEmployeeDepartmentSecondary, self).setUp()
        self.user_test = self.env.ref('base.user_demo')
        self.department = self.env["hr.department"].create(
            {"name": "Department"})
        self.secondary_department = self.env["hr.department"].create(
            {"name": "Secondary Department"})
        self.employee1 = self.env['hr.employee'].create({
            'user_id': self.env.uid,
            'name': 'Employee 1',
            'department_id': self.department.id,
            'secondary_department_ids':
                [(6, 0, [self.secondary_department.id])]
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
        })
        self.employee3 = self.env['hr.employee'].create({
            'name': 'Employee 3',
        })

    def test__assing_secondary_departments_true(self):
        self.employee2.write({
            'secondary_department_ids': [(6, 0, [self.department.id])],
            'department_id': self.secondary_department.id
        })
        self.assertNotEqual(
            self.employee1.secondary_department_ids,
            self.employee2.secondary_department_ids)
        self.assertNotEqual(
            self.employee1.department_id, self.employee2.department_id)

        with self.assertRaises(ValidationError) as e:
            self.employee3.write({
                'secondary_department_ids': [(6, 0, [self.department.id])],
                'department_id': self.department.id
            })
        self.assertEqual(
            str(e.exception),
            "('The main department must be different from the secondary departments.', None)")
