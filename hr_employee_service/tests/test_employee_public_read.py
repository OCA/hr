from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestEmployeePublicRead(BaseCommon):
    def test_read_own_employee_internal_user(self):
        """A user without HR rights reads the fields of the module it may read,
        as read([]) does, e.g. from an API client"""
        user = new_test_user(self.env, login="test-hr-employee-service")
        user.action_create_employee()
        employee = user.employee_id.with_user(user)
        fnames = ["name", "service_termination_date"]
        readable = [
            fname
            for fname in fnames
            if employee._fields[fname].is_accessible(employee.env)
        ]
        self.assertEqual(employee.read(readable)[0]["name"], user.name)
