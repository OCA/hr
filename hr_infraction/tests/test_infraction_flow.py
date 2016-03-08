# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.osv import orm


class TestInfractionFlow(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestInfractionFlow, self).setUp(*args, **kwargs)
        self.grp_employee = self.env.ref('base.group_user')
        self.grp_infraction_user = self.env.ref(
            'hr_infraction.group_infraction_user')
        self.grp_infraction_officer = self.env.ref(
            'hr_infraction.group_infraction_officer')
        self.grp_infraction_manager = self.env.ref(
            'hr_infraction.group_infraction_manager')
        self.main_company = self.env.ref(
            'base.main_company')

        # setup employee
        self.employee = self.env.ref('hr.employee_chs')
        user1_data = {
            'name': self.employee.name,
            'login': 'ds',
            'groups_id': [(6, 0, [self.grp_employee.id])],
            'email': 'chs@example.com',
            }
        self.user = self.env['res.users'].create(user1_data)
        self.employee.update({'user_id': self.user.id})

        # setup employee 2
        self.employee2 = self.env.ref('hr.employee_ngh')

        self.employee_manager = self.env.ref('hr.employee_al')
        user2_data = {
            'name': self.employee_manager.name,
            'login': 'al',
            'groups_id': [
                (6, 0, [self.grp_employee.id, self.grp_infraction_user.id])],
            'email': 'al@example.com',
            }
        self.user_manager = self.env['res.users'].create(user2_data)
        self.employee_manager.update({'user_id': self.user_manager.id})
        self.employee_manager.department_id.update(
            {'manager_id': self.employee_manager.id})

        # setup hr officer
        self.employee_hr_user = self.env.ref('hr.employee_vad')
        user3_data = {
            'name': self.employee_hr_user.name,
            'login': 'ap',
            'groups_id': [
                (6, 0, [
                    self.grp_employee.id,
                    self.grp_infraction_officer.id])],
            'email': 'ap@example.com',
            }
        self.user_hr_officer = self.env['res.users'].create(user3_data)
        self.employee_hr_user.update({'user_id': self.user_hr_officer.id})

        # setup hr manager
        self.employee_hr_manager = self.env.ref('hr.employee_fp')
        self.user_hr_manager = self.employee_hr_manager.user_id

        self.infraction_categ = self.env.ref(
            'hr_infraction.infraction_category_lt')
        self.infraction_warning = self.env.ref(
            'hr_infraction.infraction_warning_vw')

        return result

    def test_infraction_flow_1(self):
        """Test normal infraction flow
        """

        infraction_data = {
            'employee_id': self.employee.id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'company_id': self.main_company.id,
            }

        infraction = self.env['hr.infraction'].sudo(
            self.user_manager).create(infraction_data)

        self.assertIsNotNone(infraction)

        infraction.sudo(self.user_manager).button_confirm()
        self.assertEqual(infraction.state, 'confirm')

        update_data = {
            'category_id': self.infraction_categ.id,
            'warning_id': self.infraction_warning.id,
            }

        infraction.sudo(self.user_hr_officer).update(update_data)
        infraction.button_approve()
        self.assertEqual(infraction.state, 'approve')

        infraction.sudo(self.user_hr_manager).button_valid()
        self.assertEqual(infraction.state, 'valid')

    def test_infraction_flow_2(self):
        """Test infraction flow: cancel on confirm
        """

        infraction_data = {
            'employee_id': self.employee.id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'company_id': self.main_company.id,
            }

        infraction = self.env['hr.infraction'].sudo(
            self.user_manager).create(infraction_data)

        self.assertIsNotNone(infraction)

        infraction.button_confirm()
        self.assertEqual(infraction.state, 'confirm')

        infraction.button_cancel()
        self.assertEqual(infraction.state, 'cancel')

    def test_infraction_flow_3(self):
        """Test infraction flow: cancel on approve
        """

        infraction_data = {
            'employee_id': self.employee.id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'company_id': self.main_company.id,
            }

        infraction = self.env['hr.infraction'].sudo(
            self.user_manager).create(infraction_data)

        self.assertIsNotNone(infraction)

        infraction.button_confirm()
        self.assertEqual(infraction.state, 'confirm')

        update_data = {
            'category_id': self.infraction_categ.id,
            'warning_id': self.infraction_warning.id,
            }

        infraction.update(update_data)
        infraction.button_approve()
        self.assertEqual(infraction.state, 'approve')

        infraction.button_cancel()
        self.assertEqual(infraction.state, 'cancel')

    def test_infraction_flow_4(self):
        """Manager create infraction for employee on other dept.
        """

        infraction_data = {
            'employee_id': self.employee2.id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'company_id': self.main_company.id,
            }

        with self.assertRaises(orm.except_orm):
            infraction = self.env['hr.infraction'].sudo(
                self.user_manager).create(infraction_data)
            self.assertIsNone(infraction)
