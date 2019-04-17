# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEmployeeDisplayOwnInfo(TransactionCase):

    def setUp(self):
        super(TestEmployeeDisplayOwnInfo, self).setUp()

        self.user_test = self.env.ref('base.user_demo')
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee',
        })

    def test_01(self):
        self.assertFalse(self.user_test.has_group('hr.group_hr_user'))
        self.assertFalse(
            self.employee.sudo(self.user_test).employee_display_personal_data)

    def test_02(self):
        self.assertTrue(self.env.user.has_group('hr.group_hr_user'))
        self.assertTrue(self.employee.employee_display_personal_data)

    def test_03(self):
        self.employee.write({'user_id': self.user_test.id})
        self.assertFalse(self.user_test.has_group('hr.group_hr_user'))
        self.assertTrue(
            self.employee.sudo(self.user_test).employee_display_personal_data)
