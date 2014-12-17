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
    def setUp(self):
        super(test_activity_on_timesheet, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")
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

        # Create an activity
        self.vac_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'VAC')], context=context)[0]

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
            }, context=context
        )

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

        super(test_activity_on_timesheet, self).tearDown()

    def test_get_authorized_user_ids(self):
        cr, uid, context = self.cr, self.uid, self.context

        job_1 = self.job_model.browse(
            cr, uid, self.job_id, context=context)

        activity_id = job_1.activity_ids[0].id

        res = self.activity_model._get_authorized_user_ids(
            cr, uid, [activity_id],
            field_name='authorized_user_ids',
            context=context)

        self.assertTrue(self.user_id in res[activity_id])

    def test_search_activities_from_user(self):
        """
        Test the method _search_activities_from_user on activity model.

        It returns a domain [('id', 'in', [...])] to filter activities on view

        It uses the user id passed in context to find the job positions of
        the employee.
        """
        cr, uid, context = self.cr, self.uid, self.context

        res = self.activity_model._search_activities_from_user(
            cr, uid,
            obj=self.activity_model,
            field_name='authorized_user_ids',
            context={'user_id': self.user_id}
        )[0][2]

        activity_1 = self.job_model.browse(
            cr, uid, self.job_id, context=context).activity_ids[0]

        activity_2 = self.job_model.browse(
            cr, uid, self.job_2_id, context=context).activity_ids[0]

        self.assertTrue(activity_1.id in res)
        self.assertTrue(activity_2.id in res)
        self.assertTrue(self.vac_activity_id in res)
