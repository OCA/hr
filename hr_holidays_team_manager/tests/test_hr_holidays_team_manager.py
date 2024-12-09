from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools import relativedelta

from odoo.addons.base.tests.common import BaseCommon


class TestHRHolidaysTeamManager(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.emp_obj = cls.env["hr.employee"]
        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User 1",
                "login": "test",
                "groups_id": [
                    (4, cls.env.ref("hr_holidays.group_hr_holidays_user").id)
                ],
            }
        )
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Test Department",
            }
        )
        cls.department_1 = cls.env["hr.department"].create(
            {
                "name": "Test Department 2",
            }
        )
        cls.employee_1 = cls.emp_obj.create(
            {
                "name": "Test employee 1",
                "department_id": cls.department.id,
                "user_id": cls.user.id,
                "work_email": "test@test.com",
            }
        )
        cls.employee_2 = cls.emp_obj.create(
            {"name": "Test employee 2", "department_id": cls.department_1.id}
        )

        cls.employee_3 = cls.emp_obj.create(
            {
                "name": "Test employee 3",
                "department_id": cls.department.id,
                "work_email": "test@demo.com",
            }
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "requires_allocation": "no",
                "name": "Legal Leaves",
                "time_type": "leave",
            }
        )
        cls.leave_type = cls.env.ref("hr_holidays.holiday_status_unpaid")
        cls.paid_type = cls.env.ref("hr_holidays.holiday_status_cl")

    def test_hr_leave(self):
        employee_ids = (
            self.emp_obj.with_context(hr_leave=True).with_user(self.user).name_search()
        )
        self.assertEqual(len(employee_ids), 2)
        self.assertEqual(employee_ids[0][0], self.employee_1.id)
        self.assertEqual(employee_ids[1][0], self.employee_3.id)
        self.leaves = self.env["hr.leave"].create(
            {
                "date_from": fields.date.today() + relativedelta(days=-2),
                "date_to": fields.date.today() + relativedelta(days=2),
                "holiday_status_id": self.leave_type.id,
                "employee_id": self.employee_3.id,
            }
        )
        self.leaves.with_user(self.user).action_approve()

        self.assertEqual(self.leaves.state, "validate1")
        self.leaves.with_user(self.user).action_validate()
        self.assertEqual(self.leaves.state, "validate")

        leave_ids = (
            self.env["hr.leave"]
            .with_user(self.user)
            .with_context(**{"params": {"model": "hr.leave"}})
            .search([])
        )
        self.assertEqual(len(leave_ids), 1)

    def test_hr_leave_allocation(self):
        employee_ids = (
            self.emp_obj.with_context(hr_leave_allocation=True)
            .with_user(self.user)
            .name_search()
        )
        self.assertEqual(len(employee_ids), 2)
        self.assertEqual(employee_ids[0][0], self.employee_1.id)
        self.assertEqual(employee_ids[1][0], self.employee_3.id)

        self.leaves = self.env["hr.leave.allocation"].create(
            {
                "date_from": fields.date.today() + relativedelta(days=-2),
                "date_to": fields.date.today() + relativedelta(days=2),
                "holiday_status_id": self.paid_type.id,
                "employee_id": self.employee_3.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.leaves.with_user(self.user).action_confirm()

        leave_ids = (
            self.env["hr.leave.allocation"]
            .with_user(self.user)
            .with_context(**{"params": {"model": "hr.leave.allocation"}})
            .search([])
        )
        self.assertEqual(len(leave_ids), 1)
