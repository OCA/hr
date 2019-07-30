# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestNotifyEmployeeManager(TransactionCase):
    def setUp(self):
        super(TestNotifyEmployeeManager, self).setUp()
        self.hol_model = self.env['hr.leave'].with_context(import_file=True)
        # we pass 'import_file' to avoid having the manager in the activity
        # and thus be able to do the tests without the activity contamination
        self.user_model = self.env['res.users']
        self.emp_model = self.env['hr.employee']
        self.type_model = self.env['hr.leave.type']

        self.user = self.user_model.create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com'})
        self.manager = self.user_model.create({
            'name': 'Test Manager',
            'login': 'manager',
            'email': 'test.manager@example.com'})
        self.emp_manager = self.emp_model.create({
            'name': 'Test Manager',
            'user_id': self.manager.id})
        self.employee = self.emp_model.create({
            'name': 'Test employee',
            'user_id': self.user.id,
            'parent_id': self.emp_manager.id})
        self.holiday_type = self.type_model.create({
            'name': 'Leave',
            'allocation_type': 'fixed',
        })
        self.env['hr.leave.allocation'].create({
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_type.id,
            'state': 'validate',
            'number_of_days': 1.0,
        })

    def test_add_follower_1(self):
        """Tests if the employee's manager is added as follower to the leave
        request. With leave_notify_manager = False.
        """
        manager = self.manager.partner_id
        # With the configuration disabled:
        self.employee.company_id.leave_notify_manager = False
        leave = self.hol_model.sudo(self.user).create({
            'name': 'No-return-trip to Fiji',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_type.id})
        follower_set = manager in leave.message_follower_ids.mapped(
            'partner_id') if manager else False
        self.assertFalse(follower_set, "Follower added unexpectedly.")

    def test_add_follower_2(self):
        """Tests if the employee's manager is added as follower to the leave
        request. With leave_notify_manager = True.
        """
        manager = self.manager.partner_id
        # With the configuration enabled:
        self.employee.company_id.leave_notify_manager = True
        leave = self.hol_model.sudo(self.user).create({
            'name': 'No-return-trip to Bahamas',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_type.id})
        follower_set = manager in leave.message_follower_ids.mapped(
            'partner_id') if manager else False
        self.assertTrue(follower_set, "Employee's manager hasn't been added "
                                      "as follower.")
