# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.addons.hr_employee_benefit.tests.test_employee_benefit import (
    TestEmployeeBenefitBase)


class TestEmployeeBenefit(TestEmployeeBenefitBase):

    def setUp(self):

        super(TestEmployeeBenefit, self).setUp()
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry('hr.activity')
        self.worked_days_model = self.registry('hr.payslip.worked_days')
        cr, uid, context = self.cr, self.uid, self.context

        self.job_id = self.job_model.create(cr, uid, {
            'name': 'Job 1'}, context=context)

        self.activity_1_id = self.activity_model.search(cr, uid, [
            ('job_id', '=', self.job_id)], context=context)[0]

        self.job_2_id = self.job_model.create(cr, uid, {
            'name': 'Job 2'}, context=context)

        self.activity_2_id = self.activity_model.search(cr, uid, [
            ('job_id', '=', self.job_2_id)], context=context)[0]

        self.activity_3_id = self.activity_model.search(
            cr, uid, [('type', '=', 'leave')], context=context)[0]

        self.contract_model.write(cr, uid, [self.contract_id], {
            'contract_job_ids': [
                (0, 0, {
                    'job_id': self.job_id,
                    'is_main_job': True,
                }),
                (0, 0, {
                    'job_id': self.job_2_id,
                    'is_main_job': False,
                }),
            ],
        }, context=context)

        self.rate_per_hour_1_id = self.rate_model.create(cr, uid, {
            'name': 'Test',
            'category_id': self.category_ids[0],
            'amount_type': 'per_hour',
        }, context=context)

        self.rate_per_hour_2_id = self.rate_model.create(cr, uid, {
            'name': 'Test',
            'category_id': self.category_ids[1],
            'amount_type': 'per_hour',
        }, context=context)

        for line in [
            (2, 4, '2015-01-01', '2015-01-15', self.rate_per_hour_1_id),
            (3, 5, '2015-01-16', False, self.rate_per_hour_1_id),

            (6, 8, '2015-01-01', '2015-01-15', self.rate_per_hour_2_id),
            (7, 9, '2015-01-16', False, self.rate_per_hour_2_id),
        ]:
            self.rate_line_model.create(cr, uid, {
                'employee_amount': line[0],
                'employer_amount': line[1],
                'date_start': line[2],
                'date_end': line[3],
                'parent_id': line[4],
            }, context=context)

        self.benefit_model.unlink(cr, uid, self.benefit_ids, context=context)

        for line in [
            ('2015-01-01', '2015-01-10', 50, self.activity_1_id),
            ('2015-01-11', '2015-01-20', 60, self.activity_2_id),
            ('2015-01-21', '2015-01-30', 70, self.activity_3_id),
        ]:
            self.worked_days_model.create(
                cr, uid, {
                    'date_from': line[0],
                    'date_to': line[1],
                    'number_of_hours': line[2],
                    'activity_id': line[3],
                    'hourly_rate': 0,
                    'rate': 100,
                    'payslip_id': self.payslip_id,
                    'code': 'test',
                    'name': 'test',
                    'contract_id': self.contract_id,
                }, context=context)

    def test_benefits_per_hour_on_jobs(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.benefit_ids = [
            self.benefit_model.create(cr, uid, {
                'category_id': benefit[0],
                'rate_id': benefit[1],
                'date_start': benefit[2],
                'date_end': benefit[3],
                'job_id': benefit[4],
            }, context=context)
            for benefit in [
                (self.category_ids[0], self.rate_per_hour_1_id,
                    '2015-01-01', '2015-12-31', self.job_id),
                (self.category_ids[1], self.rate_per_hour_2_id,
                    '2015-01-01', '2015-12-31', self.job_2_id),
            ]
        ]

        payslip = self.compute_payslip()

        rule_1_total = (50 * 2) + (30 * 6) + (30 * 7)
        self.assertEqual(payslip['RULE_1'], rule_1_total)

        rule_2_total = (30 * 8) + (30 * 9)
        self.assertEqual(payslip['RULE_2'], rule_2_total)

    def test_benefits_per_hour_on_contract(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.benefit_ids = [
            self.benefit_model.create(cr, uid, {
                'category_id': benefit[0],
                'rate_id': benefit[1],
                'date_start': benefit[2],
                'date_end': benefit[3],
                'contract_id': self.contract_id,
            }, context=context)
            for benefit in [
                (self.category_ids[0], self.rate_per_hour_1_id,
                    '2015-01-01', '2015-12-31'),
                (self.category_ids[1], self.rate_per_hour_2_id,
                    '2015-01-01', '2015-12-31'),
            ]
        ]

        payslip = self.compute_payslip()

        rule_1_total = (
            (50 * 2) + (30 * 2) + (30 * 3) +
            (50 * 6) + (30 * 6) + (30 * 7)
        )
        self.assertEqual(payslip['RULE_1'], rule_1_total)

        rule_2_total = (
            (50 * 8) + (30 * 8) + (30 * 9)
        )
        self.assertEqual(payslip['RULE_2'], rule_2_total)
