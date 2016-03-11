# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.osv import orm


class TestAwardFlow(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestAwardFlow, self).setUp(*args, **kwargs)
        self.grp_employee = self.env.ref('base.group_user')
        self.grp_hr_officer = self.env.ref(
            'base.group_hr_user')
        self.grp_hr_manager = self.env.ref(
            'base.group_hr_manager')
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
        self.user_employee = self.env['res.users'].create(user1_data)

        # setup hr officer
        user2_data = {
            'name': 'vad',
            'login': 'vad',
            'groups_id': [
                (6, 0, [
                    self.grp_hr_officer.id])],
            'email': 'vap@example.com',
            }
        self.user_hr_officer = self.env['res.users'].create(user2_data)

        # setup hr manager
        user3_data = {
            'name': 'od',
            'login': 'od',
            'groups_id': [
                (6, 0, [
                    self.grp_hr_manager.id])],
            'email': 'od@example.com',
            }
        self.user_hr_manager = self.env['res.users'].create(user3_data)

        self.award_type = self.env.ref(
            'hr_employee_award.award_type_eom')

        return result

    def test_award_flow_1(self):
        """Test normal award flow
        draft -> issued
        create & confirm by HR Officer
        approved & confirm by HR Manager
        """

        award_data = {
            'employee_id': self.employee.id,
            'award_type_id': self.award_type.id,
            }

        award = self.env['hr.award'].sudo(
            self.user_hr_officer).create(award_data)

        self.assertIsNotNone(award)

        award.sudo(self.user_hr_officer).button_confirm()
        self.assertEqual(award.state, 'confirmed')

        award.sudo(self.user_hr_officer).button_approve()
        self.assertEqual(award.state, 'approved')

        update_data = {
            'date_issued': datetime.now().strftime('%Y-%m-%d'),
            }

        award.sudo(self.user_hr_manager).update(update_data)
        award.sudo(self.user_hr_manager).button_issue()
        self.assertEqual(award.state, 'issued')
        self.assertNotEqual(award.state, '/')

    def test_award_flow_2(self):
        """Test award flow with cancellation #1
        draft -> confirmed -> Cancelled -> draft
        all by HR Officer
        """

        award_data = {
            'employee_id': self.employee.id,
            'award_type_id': self.award_type.id,
            }

        award = self.env['hr.award'].sudo(
            self.user_hr_officer).create(award_data)

        self.assertIsNotNone(award)

        award.sudo(self.user_hr_officer).button_confirm()
        self.assertEqual(award.state, 'confirmed')

        award.sudo(self.user_hr_officer).button_cancel()
        self.assertEqual(award.state, 'cancelled')

        award.sudo(self.user_hr_officer).button_restart()
        self.assertEqual(award.state, 'draft')

    def test_award_flow_3(self):
        """Test award flow with cancellation #2
        draft -> approved -> Cancelled -> draft
        Create & confirm by HR Officer
        Approve & cancel by HR Manager
        """

        award_data = {
            'employee_id': self.employee.id,
            'award_type_id': self.award_type.id,
            }

        award = self.env['hr.award'].sudo(
            self.user_hr_officer).create(award_data)

        self.assertIsNotNone(award)

        award.sudo(self.user_hr_officer).button_confirm()
        self.assertEqual(award.state, 'confirmed')

        award.sudo(self.user_hr_manager).button_approve()
        self.assertEqual(award.state, 'approved')

        award.sudo(self.user_hr_officer).button_cancel()
        self.assertEqual(award.state, 'cancelled')

        award.sudo(self.user_hr_officer).button_restart()
        self.assertEqual(award.state, 'draft')

    def test_award_flow_4(self):
        """Test award flow with cancellation #3
        draft -> issued -> Cancelled -> draft
        Create & confirm by HR Officer
        Approve, issued, and cancel by HR Manager
        """

        award_data = {
            'employee_id': self.employee.id,
            'award_type_id': self.award_type.id,
            }

        award = self.env['hr.award'].sudo(
            self.user_hr_officer).create(award_data)

        self.assertIsNotNone(award)

        award.sudo(self.user_hr_officer).button_confirm()
        self.assertEqual(award.state, 'confirmed')

        award.sudo(self.user_hr_manager).button_approve()
        self.assertEqual(award.state, 'approved')

        update_data = {
            'date_issued': datetime.now().strftime('%Y-%m-%d'),
            }
        award.sudo(self.user_hr_manager).update(update_data)
        award.sudo(self.user_hr_manager).button_issue()
        self.assertEqual(award.state, 'issued')
        self.assertNotEqual(award.state, '/')

        award.sudo(self.user_hr_officer).button_cancel()
        self.assertEqual(award.state, 'cancelled')

        award.sudo(self.user_hr_officer).button_restart()
        self.assertEqual(award.state, 'draft')
        self.assertNotEqual(award.state, '/')

    def test_award_flow_5(self):
        """Test exception when award create by user
        """

        award_data = {
            'employee_id': self.employee.id,
            'award_type_id': self.award_type.id,
            }

        with self.assertRaises(orm.except_orm):
            award = self.env['hr.award'].sudo(
                self.user_employee).create(award_data)
            self.assertIsNone(award)
