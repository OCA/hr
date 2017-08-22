# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestNotifyEmployeeManager(TransactionCase):
    def setUp(self):
        super(TestNotifyEmployeeManager, self).setUp()
        self.hol_model = self.env['hr.holidays']
        self.user_model = self.env['res.users']
        self.emp_model = self.env['hr.employee']
        self.type_model = self.env['hr.holidays.status']

        self.user = self.user_model.create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com'})
        self.manager = self.user_model.create({
            'name': 'Test Manager',
            'login': 'manager',
            'email': 'test.manager@example.com'})
        emp_manager = self.emp_model.create({
            'name': 'Test Manager',
            'user_id': self.manager.id})
        self.employee = self.emp_model.create({
            'name': 'Test employee',
            'user_id': self.user.id,
            'parent_id': emp_manager.id})
        self.holiday_type = self.type_model.create({'name': 'Leave'})

    def test_add_follower(self):
        """Tests if the employee's manager is added as follower to the leave
        request.
        """
        manager = self.manager.partner_id
        # With the configuration disabled:
        self.employee.company_id.leave_notify_manager = False
        leave = self.hol_model.sudo(self.user).create({
            'name': 'No-return-trip to Fiji',
            'holiday_status_id': self.holiday_type.id})
        follower_set = manager in leave.message_follower_ids.mapped(
            'partner_id') if manager else False
        self.assertFalse(follower_set, "Follower added unexpectedly.")
        # With the configuration enabled:
        self.employee.company_id.leave_notify_manager = True
        leave = self.hol_model.sudo(self.user).create({
            'name': 'No-return-trip to Bahamas',
            'holiday_status_id': self.holiday_type.id})
        follower_set = manager in leave.message_follower_ids.mapped(
            'partner_id') if manager else False
        self.assertTrue(follower_set, "Employee's manager hasn't been added "
                                      "as follower.")
