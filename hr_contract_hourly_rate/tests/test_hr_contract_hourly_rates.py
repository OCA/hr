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

from openerp.tests.common import TransactionCase
from openerp import exceptions


class test_contract_hourly_rate(TransactionCase):
    def setUp(self):
        super(test_contract_hourly_rate, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.user_model = self.env["res.users"]
        self.contract_model = self.env["hr.contract"]
        self.job_model = self.env["hr.job"]
        self.rate_class_model = self.env["hr.hourly.rate.class"]

        # Create an employee
        self.employee_id = self.employee_model.create({'name': 'Employee 1'})

        # Create 3 jobs
        self.job_id = self.job_model.create({'name': 'Job 1'})

        self.job_2_id = self.job_model.create({'name': 'Job 2'})

        self.job_3_id = self.job_model.create({'name': 'Job 3'})

        # Create 3 hourly rate classes
        self.rate_class_id = self.rate_class_model.create(
            {
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
            }
        )

        self.rate_class_2_id = self.rate_class_model.create(
            {
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
            }
        )

        self.rate_class_3_id = self.rate_class_model.create(
            {
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
            }
        )

        # Create a contract
        self.contract_id = self.contract_model.create(
            {
                'employee_id': self.employee_id.id,
                'name': 'Contract 1',
                'wage': 50000,
                'salary_computation_method': 'hourly_rate',
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': self.job_id.id,
                        'is_main_job': False,
                        'hourly_rate_class_id': self.rate_class_id.id,
                    }),
                    (0, 0, {
                        'job_id': self.job_2_id.id,
                        'is_main_job': True,
                        'hourly_rate_class_id': self.rate_class_2_id.id,
                    }),
                    (0, 0, {
                        'job_id': self.job_3_id.id,
                        'is_main_job': False,
                        'hourly_rate_class_id': self.rate_class_3_id.id,
                    }),
                ],
            }
        )

    def test_check_overlapping_dates(self):
        """
        test the _check_overlapping_dates constraint
        on hourly rate class
        """
        # Should all return the same result
        for dates in [('2013-01-01', '2014-01-01'),
                      ('2014-12-31', '2015-12-31'),
                      ('2014-06-01', '2014-07-31')]:
            self.assertRaises(
                exceptions.ValidationError, self.rate_class_model.write,
                [self.rate_class_id.id], {
                    'line_ids': [
                        (0, 0, {
                            'date_start': dates[0],
                            'date_end': dates[1],
                            'rate': 15,
                        }),
                    ],
                }
            )

    def test_check_has_hourly_rate_class(self):
        """
        test the _check_overlapping_dates constraint
        on contract
        """
        job_id = self.job_model.create({'name': 'Job 4'})

        self.assertRaises(
            exceptions.ValidationError, self.contract_model.write,
            [self.contract_id.id], {
                'contract_job_ids': [
                    (0, 0, {
                        'job_id': job_id.id,
                        'is_main_job': False,
                        'hourly_rate_class_id': False,
                    }),
                ],
            }
        )

        self.job_model.unlink([job_id.id])

    def test_get_job_hourly_rate(self):
        """
        test the method get_job_hourly_rate with job_id argument
        """
        # Should all return the same result
        for dates in [('2014-02-01', '2014-02-10'),
                      ('2014-01-01', '2014-06-30')]:
            res = self.contract_id.get_job_hourly_rate(
                dates[0], dates[1], job_id=self.job_3_id.id, main_job=False)

            self.assertTrue(res == 20)

        # Should all return the same result
        for dates in [('2014-08-10', '2014-08-20'),
                      ('2014-07-01', '2014-12-31')]:
            res = self.contract_id.get_job_hourly_rate(
                dates[0], dates[1], job_id=self.job_3_id.id, main_job=False)

            self.assertTrue(res == 25)

    def test_get_job_hourly_rate_main_job(self):
        """
        test the method get_job_hourly_rate with main_job argument
        """
        # Should all return the same result
        for dates in [('2014-02-01', '2014-02-10'),
                      ('2014-01-01', '2014-06-30')]:
            res = self.contract_id.get_job_hourly_rate(
                dates[0], dates[1], job_id=False, main_job=True)

            self.assertTrue(res == 30)

        # Should all return the same result
        for dates in [('2014-08-10', '2014-08-20'),
                      ('2014-07-01', '2014-12-31')]:
            res = self.contract_id.get_job_hourly_rate(
                dates[0], dates[1], job_id=False, main_job=True)

            self.assertTrue(res == 35)

            self.assertRaises(
                exceptions.ValidationError, self.rate_class_model.write,
                [self.rate_class_id.id],
                {
                    'line_ids': [
                        (0, 0, {
                            'date_start': dates[0],
                            'date_end': dates[1],
                            'rate': 15,
                        }),
                    ],
                }
            )
