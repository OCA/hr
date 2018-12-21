# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrHolidaysSecurity(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.employee_admin = self.SudoHrEmployee.browse(
            self.ref('hr.employee_admin')
        )
        self.employee_qdp = self.SudoHrEmployee.browse(
            self.ref('hr.employee_qdp')
        )
        self.HrLeave = self.env['hr.leave']
        self.SudoHrLeave = self.HrLeave.sudo()
        self.hr_holidays_employee1_cl = self.SudoHrLeave.browse(
            self.ref('hr_holidays.hr_holidays_employee1_cl')
        )

    def test_1(self):
        leave_admin = self.hr_holidays_employee1_cl.sudo(
            self.employee_admin.user_id.id
        )
        leave_admin._compute_can_view_name()
        self.assertTrue(leave_admin.can_view_name)

        leave_qdp = self.hr_holidays_employee1_cl.sudo(
            self.employee_qdp.user_id.id
        )
        leave_qdp._compute_can_view_name()
        self.assertFalse(leave_qdp.can_view_name)
