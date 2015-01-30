# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common


class test_activity_on_timesheet(common.TransactionCase):
    def get_activity_id(self, job_id):
        job = self.job_model.browse(
            self.cr, self.uid, job_id, context=self.context)
        return job.activity_ids[0].id

    def setUp(self):
        super(test_activity_on_timesheet, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")
        self.account_model = self.registry("account.analytic.account")
        self.timesheet_model = self.registry("hr.analytic.timesheet")
        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create a user
        self.user_id = self.user_model.create(
            cr, uid, {
                'name': 'User 1',
                'login': 'test',
                'password': 'test',
            }, context=context)

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'user_id': self.user_id
            }, context=context)

        # Create 3 jobs
        self.job_id = self.job_model.create(
            cr, uid, {'name': 'Job 1'}, context=context)

        self.job_2_id = self.job_model.create(
            cr, uid, {'name': 'Job 2'}, context=context)

        self.job_3_id = self.job_model.create(
            cr, uid, {'name': 'Job 3'}, context=context)

        # Vacations activity
        self.vac_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'VAC')], context=context)[0]

        # Sick leaves activity
        self.sl_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'SL')], context=context)[0]

        # Create a contract
        self.contract_id = self.contract_model.create(
            self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'date_start': '2014-01-01',
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'is_main_job': False,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id,
                        'is_main_job': True,
                    }),
                ],
            }, context=context)

        self.account_id = self.account_model.create(
            self.cr, self.uid, {
                'type': 'normal',
                'use_timesheets': True,
                'name': 'Account 1',
                'activity_type': 'job',
                'authorized_activity_ids': [(6, 0, [
                    self.get_activity_id(self.job_2_id),
                    self.get_activity_id(self.job_3_id),
                ])],
            }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)

        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        self.user_model.unlink(
            cr, uid, [self.user_id], context=context)

        self.job_model.unlink(
            cr, uid, [self.job_id, self.job_2_id, self.job_3_id],
            context=context)

        self.account_model.unlink(
            cr, uid, [self.account_id], context=context)

        super(test_activity_on_timesheet, self).tearDown()

    def test_on_change_account_id_not_authorized(self):
        """
        Test on_change_account_id when the given activity
        is not authorized on the analytic account
        """
        cr, uid, context = self.cr, self.uid, self.context

        activity_id = self.get_activity_id(self.job_id)

        res = self.timesheet_model.on_change_account_id(
            cr, uid, [self.account_id], self.account_id,
            user_id=self.user_id, activity_id=activity_id,
            context=context)

        self.assertEqual(res['value']['activity_id'], False)

    def test_on_change_account_id_authorized(self):
        """
        Test on_change_account_id when the given activity
        is authorized on the analytic account
        """
        cr, uid, context = self.cr, self.uid, self.context

        activity_id = self.get_activity_id(self.job_2_id)

        res = self.timesheet_model.on_change_account_id(
            cr, uid, [self.account_id], self.account_id,
            user_id=self.user_id, activity_id=activity_id,
            context=context)

        self.assertEqual(res['value']['activity_id'], activity_id)

    def test_on_change_account_id_no_activity(self):
        """
        Test on_change_account_id when no activity is given in parameter
        """
        cr, uid, context = self.cr, self.uid, self.context

        res = self.timesheet_model.on_change_account_id(
            cr, uid, [self.account_id], self.account_id,
            user_id=self.user_id, activity_id=False,
            context=context)

        self.assertEqual(res['value']['activity_id'], False)

    def test_search_activities(self):
        """
        Test the method _search_activities_from_user on activity model.

        It returns a domain [('id', 'in', [...])] to filter activities on view
        """
        cr, uid, = self.cr, self.uid

        res = self.activity_model._search_activities_from_user(
            cr, uid,
            obj=self.activity_model,
            field_name='authorized_user_ids',
            context={'user_id': self.user_id, 'account_id': self.account_id}
        )[0][2]

        activity_id = self.get_activity_id(self.job_id)
        activity_2_id = self.get_activity_id(self.job_2_id)
        activity_3_id = self.get_activity_id(self.job_3_id)

        self.assertIn(activity_2_id, res)

        # Job 1 is not in the account's authorized activities
        # Job 3 is not on the employee's contract
        self.assertNotIn(activity_id, res)
        self.assertNotIn(activity_3_id, res)

        # Leaves are not allowed for the analytic account
        self.assertNotIn(self.vac_activity_id, res)
        self.assertNotIn(self.sl_activity_id, res)

    def test_search_activities_leaves(self):
        """
        Test the method _search_activities_from_user with leave types
        authorized on the analytic account
        It returns a domain [('id', 'in', [...])] to filter activities on view
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.account_model.write(
            cr, uid, [self.account_id], {
                'activity_type': 'leave',
                'authorized_activity_ids': [(6, 0, [
                    self.vac_activity_id
                ])]
            }, context=context)

        res = self.activity_model._search_activities_from_user(
            cr, uid,
            obj=self.activity_model,
            field_name='authorized_user_ids',
            context={'user_id': self.user_id, 'account_id': self.account_id}
        )[0][2]

        activity_id = self.get_activity_id(self.job_id)
        activity_2_id = self.get_activity_id(self.job_2_id)
        activity_3_id = self.get_activity_id(self.job_3_id)

        self.assertIn(self.vac_activity_id, res)

        # sl is not in the list of authorized activities
        self.assertNotIn(self.sl_activity_id, res)

        # Job positions are not allowed for the analytic account
        self.assertNotIn(activity_id, res)
        self.assertNotIn(activity_2_id, res)
        self.assertNotIn(activity_3_id, res)

    def test_search_activities_no_activity_on_account(self):
        """
        Test the method _search_activities_from_user on activity model
        with no authorized activities on the analytic account

        It returns a domain [('id', 'in', [...])] to filter activities on view
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.account_model.write(
            cr, uid, [self.account_id], {
                'activity_type': 'job',
                'authorized_activity_ids': [(6, 0, [])],
            }, context=context)

        res = self.activity_model._search_activities_from_user(
            cr, uid,
            obj=self.activity_model,
            field_name='authorized_user_ids',
            context={'user_id': self.user_id, 'account_id': self.account_id}
        )[0][2]

        activity_id = self.get_activity_id(self.job_id)
        activity_2_id = self.get_activity_id(self.job_2_id)
        activity_3_id = self.get_activity_id(self.job_3_id)

        self.assertIn(activity_id, res)
        self.assertIn(activity_2_id, res)

        # The job 3 does not appear on the employee's contract
        self.assertNotIn(activity_3_id, res)

        # Leaves are not allowed for the analytic account
        self.assertNotIn(self.vac_activity_id, res)
        self.assertNotIn(self.sl_activity_id, res)
