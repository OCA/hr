# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 - 2015 Savoir-faire Linux. All Rights Reserved.
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


class test_worked_days_from_timesheet(common.TransactionCase):
    def setUp(self):
        super(test_worked_days_from_timesheet, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.ts_sheet_model = self.registry("hr_timesheet_sheet.sheet")
        self.timesheet_model = self.registry("hr.analytic.timesheet")
        self.account_model = self.registry("account.analytic.account")
        self.run_wizard_model = self.registry("hr.payslip.employees")
        self.journal_model = self.registry("account.analytic.journal")
        self.rate_class_model = self.registry("hr.hourly.rate.class")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")

        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create two user
        self.user_id = self.user_model.create(
            cr, uid, {
                'name': 'User 1',
                'login': 'test',
                'password': 'test',
            }, context=context)

        # Create two employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'user_id': self.user_id,
            }, context=context)

        # Create an analytic account
        self.account_id = self.account_model.create(
            cr, uid, {
                'name': 'Account 1',
                'type': 'normal',
                'use_timesheets': True,
            }, context=context)

        # Create 3 jobs
        self.job_id = self.job_model.create(
            cr, uid, {'name': 'Job 1'}, context=context)

        self.job_2_id = self.job_model.create(
            cr, uid, {'name': 'Job 2'}, context=context)

        self.job_3_id = self.job_model.create(
            cr, uid, {'name': 'Job 3'}, context=context)

        # Get the activity related to the jobs
        self.job_1_activity_id = self.job_model.browse(
            cr, uid, self.job_id, context=context).activity_ids[0].id

        self.job_2_activity_id = self.job_model.browse(
            cr, uid, self.job_2_id, context=context).activity_ids[0].id

        self.job_3_activity_id = self.job_model.browse(
            cr, uid, self.job_3_id, context=context).activity_ids[0].id

        # Create an activity
        self.vac_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'VAC')], context=context)[0]

        # Create hourly rate classes
        self.rate_class_id = self.rate_class_model.create(
            cr, uid, {
                'name': 'Test',
                'line_ids': [
                    (0, 0, {
                        'date_start': '2014-01-01',
                        'date_end': '2014-05-31',
                        'rate': 20,
                    }),
                    (0, 0, {
                        'date_start': '2014-06-01',
                        'date_end': '2014-12-31',
                        'rate': 25,
                    })
                ],
            }, context=context)

        self.rate_class_2_id = self.rate_class_model.create(
            cr, uid, {
                'name': 'Test',
                'line_ids': [
                    (0, 0, {
                        'date_start': '2014-01-01',
                        'date_end': '2014-05-31',
                        'rate': 30,
                    }),
                    (0, 0, {
                        'date_start': '2014-06-01',
                        'date_end': '2014-12-31',
                        'rate': 35,
                    })
                ],
            }, context=context)

        # Create a contract for the employee
        self.contract_id = self.contract_model.create(
            self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'date_start': '2014-01-01',
                'salary_computation_method': 'hourly_rate',
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'hourly_rate_class_id': self.rate_class_id,
                        'is_main_job': False,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id,
                        'hourly_rate_class_id': self.rate_class_2_id,
                        'is_main_job': True,
                    })

                ],
            }, context=context)

        # Create timesheets
        self.ts_sheet_ids = [
            self.ts_sheet_model.create(
                cr, uid,
                {
                    'employee_id': ts[0],
                    'date_from': ts[1],
                    'date_to': ts[2],
                },
                context=context,
            ) for ts in [
                (self.employee_id, '2014-06-01', '2014-06-07'),
                (self.employee_id, '2014-06-08', '2014-06-14'),
                (self.employee_id, '2014-06-15', '2014-06-21'),
                (self.employee_id, '2014-06-22', '2014-06-28'),
            ]
        ]

        self.journal_id = self.journal_model.search(
            cr, uid, [('code', '=', 'TS')], context=context)[0]

        self.timesheet_ids = [
            self.timesheet_model.create(
                cr, uid, {
                    'date': ts[0],
                    'user_id': ts[1],
                    'name': 'ddd',
                    'account_id': self.account_id,
                    'unit_amount': ts[2],
                    'activity_id': ts[3],
                    'journal_id': self.journal_id,
                },
                context=context,
            ) for ts in [
                ('2014-06-01', self.user_id, 3, self.vac_activity_id),
                ('2014-06-02', self.user_id, 5, self.job_2_activity_id),
                ('2014-06-08', self.user_id, 7, self.job_1_activity_id),

                ('2014-06-09', self.user_id, 8, self.job_1_activity_id),
                ('2014-06-14', self.user_id, 9, self.job_2_activity_id),
                ('2014-06-15', self.user_id, 11, self.vac_activity_id),
                ('2014-06-16', self.user_id, 13, self.job_1_activity_id),
                ('2014-06-16', self.user_id, 14, self.job_1_activity_id),
                ('2014-06-20', self.user_id, 15, self.job_2_activity_id),

                ('2014-06-21', self.user_id, 17, self.job_2_activity_id),
                ('2014-06-22', self.user_id, 19, self.job_2_activity_id),
            ]
        ]

        self.ts_sheet_model.write(
            cr, uid, self.ts_sheet_ids, {'state': 'done'}, context=context)

    def make_payslip(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_id = self.payslip_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'contract_id': self.contract_id,
                'date_from': '2014-06-09',
                'date_to': '2014-06-20',
            }, context=context)

        self.payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        self.payslip.import_worked_days()

        self.payslip.refresh()

        self.assertTrue(len(self.payslip.worked_days_line_ids), 6)

    def test_import_worked_days_hourly_rate(self):
        """
        Test the payslip method import_worked_days
        when the employee is paid by hourly rates
        """
        self.make_payslip()

        sub_totals = {
            self.job_1_activity_id: 0,
            self.job_2_activity_id: 0,
            self.vac_activity_id: 0,
        }

        for wd in self.payslip.worked_days_line_ids:
            sub_totals[wd.activity_id.id] += wd.total

        self.assertEqual(
            sub_totals[self.job_1_activity_id],
            (8 + 13 + 14) * 25)

        self.assertEqual(
            sub_totals[self.job_2_activity_id],
            (9 + 15) * 35)

        # The employee takes 11 hours of vacations
        # his main job's hourly rate is taken (35 / hour)
        self.assertEqual(
            sub_totals[self.vac_activity_id],
            11 * 35)

    def test_import_worked_days_wage(self):
        """
        Test the payslip method import_worked_days
        when the employee is paid by wage
        """
        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'salary_computation_method': 'wage',
            }, context=self.context)

        self.make_payslip()

        # Because the employee is paid by wage, the hourly rate
        # will be 0. Instead, we check the number of hours.
        sub_totals = {
            self.job_1_activity_id: 0,
            self.job_2_activity_id: 0,
            self.vac_activity_id: 0,
        }

        for wd in self.payslip.worked_days_line_ids:
            sub_totals[wd.activity_id.id] += wd.number_of_hours

        self.assertEqual(
            sub_totals[self.job_1_activity_id], 8 + 13 + 14)

        self.assertEqual(
            sub_totals[self.job_2_activity_id], 9 + 15)

        self.assertEqual(
            sub_totals[self.vac_activity_id], 11)
