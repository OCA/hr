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
from openerp.osv.orm import except_orm


class test_contract_hourly_rate(common.TransactionCase):
    def setUp(self):
        super(test_contract_hourly_rate, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.rate_class_model = self.registry("hr.hourly.rate.class")
        self.context = self.user_model.context_get(self.cr, self.uid)

        # Create an employee
        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context)

        # Create 3 jobs
        self.job_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 1'}, context=self.context)

        self.job_2_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 2'}, context=self.context)

        self.job_3_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 3'}, context=self.context)

        # Create 2 hourly rate classes
        self.rate_class_id = self.rate_class_model.create(
            self.cr, self.uid, {
                'name': 'Test',
                'line_ids': [
                    (0, 0, {
                        'date_start': '2014-01-01',
                        'date_end': '2014-06-30',
                        'rate': 40,
                    }),
                    (0, 0, {
                        'date_start': '2014-07-01',
                        'date_end': '2014-12-31',
                        'rate': 45,
                    }),
                ],
            }, context=self.context
        )

        self.rate_class_2_id = self.rate_class_model.create(
            self.cr, self.uid, {
                'name': 'Test',
                'line_ids': [
                    (0, 0, {
                        'date_start': '2014-01-01',
                        'date_end': '2014-06-30',
                        'rate': 30,
                    }),
                    (0, 0, {
                        'date_start': '2014-07-01',
                        'date_end': '2014-12-31',
                        'rate': 35,
                    }),
                ],
            }, context=self.context
        )

        self.rate_class_3_id = self.rate_class_model.create(
            self.cr, self.uid, {
                'name': 'Test',
                'line_ids': [
                    (0, 0, {
                        'date_start': '2014-01-01',
                        'date_end': '2014-06-30',
                        'rate': 20,
                    }),
                    (0, 0, {
                        'date_start': '2014-07-01',
                        'date_end': '2014-12-31',
                        'rate': 25,
                    }),
                ],
            }, context=self.context
        )

        # Create a contract
        self.contract_id = self.contract_model.create(
            self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'salary_computation_method': 'hourly_rate',
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id,
                        'is_main_job': False,
                        'hourly_rate_class_id': self.rate_class_id,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id,
                        'is_main_job': True,
                        'hourly_rate_class_id': self.rate_class_2_id,
                    }),
                    (0, 0, {
                        'job_id': self.job_3_id,
                        'is_main_job': False,
                        'hourly_rate_class_id': self.rate_class_3_id,
                    }),
                ],
            }, context=self.context
        )

        self.contract_model.write(
            self.cr, self.uid, [self.contract_id], {
                'job_id': self.job_id
            }, context=self.context)

    def tearDown(self):
        self.contract_model.unlink(
            self.cr, self.uid, [self.contract_id], context=self.context)

        self.employee_model.unlink(
            self.cr, self.uid, [self.employee_id], context=self.context)

        self.rate_class_model.unlink(
            self.cr, self.uid,
            [self.rate_class_id, self.rate_class_2_id, self.rate_class_3_id],
            context=self.context)

        self.job_model.unlink(
            self.cr, self.uid,
            [self.job_id, self.job_2_id, self.job_3_id],
            context=self.context)

        super(test_contract_hourly_rate, self).tearDown()

    def test_check_overlapping_dates(self):
        """
        test the _check_overlapping_dates constraint
        on hourly rate class
        """
        for dates in [
            # Should all return the same result
            ('2013-01-01', '2014-01-01'),
            ('2014-12-31', '2015-12-31'),
            ('2014-06-01', '2014-07-31'),
        ]:
            self.assertRaises(
                except_orm, self.rate_class_model.write,
                self.cr, self.uid, [self.rate_class_id], {
                    'line_ids': [
                        (0, 0, {
                            'date_start': dates[0],
                            'date_end': dates[1],
                            'rate': 15,
                        }),
                    ],
                }, context=self.context
            )

    def test_check_has_hourly_rate_class(self):
        """
        test the _check_overlapping_dates constraint
        on contract
        """
        job_id = self.job_model.create(
            self.cr, self.uid, {'name': 'Job 4'}, context=self.context)

        self.assertRaises(
            except_orm, self.contract_model.write,
            self.cr, self.uid, [self.contract_id], {
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': job_id,
                        'is_main_job': False,
                        'hourly_rate_class_id': False,
                    }),
                ],
            }, context=self.context
        )

        self.job_model.unlink(
            self.cr, self.uid, [job_id], context=self.context)

    def test_get_job_hourly_rate(self):
        """
        test the method get_job_hourly_rate with job_id argument
        """
        for dates in [
            # Should all return the same result
            ('2014-02-01', '2014-02-10'),
            ('2014-01-01', '2014-06-30'),
        ]:
            res = self.contract_model.get_job_hourly_rate(
                self.cr, self.uid, dates[0], dates[1],
                self.contract_id, job_id=self.job_3_id, main_job=False,
                context=self.context)

            self.assertTrue(res == 20)

        for dates in [
            # Should all return the same result
            ('2014-08-10', '2014-08-20'),
            ('2014-07-01', '2014-12-31'),
        ]:
            res = self.contract_model.get_job_hourly_rate(
                self.cr, self.uid, dates[0], dates[1],
                self.contract_id, job_id=self.job_3_id, main_job=False,
                context=self.context)

            self.assertTrue(res == 25)

    def test_get_job_hourly_rate_main_job(self):
        """
        test the method get_job_hourly_rate with main_job argument
        """
        for dates in [
            # Should all return the same result
            ('2014-02-01', '2014-02-10'),
            ('2014-01-01', '2014-06-30'),
        ]:
            res = self.contract_model.get_job_hourly_rate(
                self.cr, self.uid, dates[0], dates[1],
                self.contract_id, job_id=False, main_job=True,
                context=self.context)

            self.assertTrue(res == 30)

        for dates in [
            # Should all return the same result
            ('2014-08-10', '2014-08-20'),
            ('2014-07-01', '2014-12-31'),
        ]:
            res = self.contract_model.get_job_hourly_rate(
                self.cr, self.uid, dates[0], dates[1],
                self.contract_id, job_id=False, main_job=True,
                context=self.context)

            self.assertTrue(res == 35)

            self.assertRaises(
                except_orm, self.rate_class_model.write,
                self.cr, self.uid, [self.rate_class_id], {
                    'line_ids': [
                        (0, 0, {
                            'date_start': dates[0],
                            'date_end': dates[1],
                            'rate': 15,
                        }),
                    ],
                }, context=self.context
            )
