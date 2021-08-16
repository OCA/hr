# Copyright 2021 Som Energia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common

from datetime import datetime
from dateutil.relativedelta import relativedelta

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
            'department_ids': [(6,0,[self.department.id])]
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
            'department_id': self.department.id,
            'department_ids': [(6,0,[self.department.id])]
        })
        self.employee3 = self.env['hr.employee'].create({
            'name': 'Employee 3',
        })

    def test_leave__common_department_with_user_True(self):
        leave = self.env["hr.leave"].create({"employee_id": self.employee2.id})
        self.assertTrue(leave.common_department_with_user)

    def test_leave__common_department_with_user_False(self):
        leave = self.env["hr.leave"].create({"employee_id": self.employee3.id})
        self.assertFalse(leave.common_department_with_user)

    def test_leave__common_department_single_department_field_with_user_TrueFalse(self):
        leave = self.env["hr.leave"].create({"employee_id": self.employee3.id})
        self.assertFalse(leave.common_department_with_user)
        self.Employee.write({'id': self.employee3.id, 'department_id': self.department.id})
        self.assertFalse(leave.common_department_with_user)

    def test_leave__common_department_multiple_department_field_with_user_TrueFalse(self):
        leave = self.env["hr.leave"].create({"employee_id": self.employee3.id})
        self.assertFalse(leave.common_department_with_user)
        self.employee3.write({'department_ids': [(6,0,[self.department.id])]})
        self.assertTrue(leave.common_department_with_user)