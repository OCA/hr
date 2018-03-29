# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from datetime import date, time, datetime
from dateutil.relativedelta import relativedelta

from openerp.tests import common
from openerp import fields


class TestHolidaysEvaluateAllocation(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysEvaluateAllocation, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.holiday_status_model = self.env['hr.holidays.status']
        self.holiday_model = self.env['hr.holidays']
        self.rule_model = self.env['hr.holidays.evaluation.rule']
        self.ruleset_model = self.env['hr.holidays.evaluation.ruleset']

        self.company = self.env.ref('base.main_company')

        # Create fixed ruleset and rules
        self.ruleset_fixed = self.ruleset_model.create({
            'name': 'Ruleset',
            'mode': 'first',
            'period': 'year',
        })
        self.rule_model.create(
            {
                'name': 'Rule',
                'sequence': 1,
                'ruleset_id': self.ruleset_fixed.id,
                'condition_select': 'none',
                'amount': 20
            }
        )

        # Create range ruleset and rules
        self.ruleset_range = self.ruleset_model.create({
            'name': 'Ruleset',
            'mode': 'first',
            'period': 'year',
        })
        range_values = (
            (0, 1, 0),
            (1, 3, 24),
            (3, 5, 32),
        )
        sequence = 0
        for values in range_values:
            self.rule_model.create(
                {
                    'name': 'Rule',
                    'ruleset_id': self.ruleset_range.id,
                    'sequence': sequence,
                    'condition_range': 'employee.length_of_service',
                    'condition_select': 'range',
                    'condition_range_min': values[0],
                    'condition_range_max': values[1],
                    'amount': values[2]
                }
            )
            sequence += 1

        # Create python ruleset and rules
        self.ruleset_python = self.ruleset_model.create({
            'name': 'Ruleset',
            'mode': 'first',
            'period': 'year',
        })
        python_values = (
            ('result = employee.length_of_service >= 0 '
             'and employee.length_of_service <= 1', 0),
            ('result = employee.length_of_service >= 1 '
             'and employee.length_of_service <= 3', 24),
            ('result = employee.length_of_service >= 3 '
             'and employee.length_of_service <= 5', 32),
        )
        sequence = 0
        for values in python_values:
            self.rule_model.create(
                {
                    'name': 'Rule',
                    'ruleset_id': self.ruleset_python.id,
                    'sequence': sequence,
                    'condition_select': 'python',
                    'condition_python': values[0],
                    'amount': values[1],
                }
            )
            sequence += 1

        # create employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        # create leave type
        self.holiday_status = self.holiday_status_model.create(
            {
                'name': 'Holiday Type',
                'limit': False,
            }
        )

        self.company.legal_holidays_status_id = self.holiday_status.id

    def test_allocation_fixed(self):
        # let's test fixed allocation
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_allocation_range(self):
        # let's test range allocation
        self.holiday_status.write({'ruleset_id': self.ruleset_range.id})
        # employee less than a year old
        self.employee.write({'initial_employment_date':
                             str(date.today() - relativedelta(days=60))})
        self.assertEqual(self.employee.remaining_leaves, 0)

        # employee more than a year old
        self.employee.write({'initial_employment_date':
                             str(date.today()
                                 - relativedelta(years=1, days=1))})
        self.assertEqual(self.employee.remaining_leaves, 24)

        # employee more than three year old
        self.employee.write({'initial_employment_date':
                             str(date.today() - relativedelta(years=4))})
        self.assertEqual(self.employee.remaining_leaves, 32)

    def test_allocation_python(self):
        # let's test python allocation
        self.holiday_status.write({'ruleset_id': self.ruleset_python.id})
        # employee less than a year old
        self.employee.write({'initial_employment_date':
                             str(date.today() - relativedelta(days=60))})
        self.assertEqual(self.employee.remaining_leaves, 0)

        # employee more than a year old
        self.employee.write({'initial_employment_date':
                            str(date.today()
                                - relativedelta(years=1, days=1))})
        self.assertEqual(self.employee.remaining_leaves, 24)

        # employee more than three year old
        self.employee.write({'initial_employment_date':
                            str(date.today() - relativedelta(years=4))})
        self.assertEqual(self.employee.remaining_leaves, 32)

    def _test_allocation_mode_helper(self):
        self.rule_model.create(
            {
                'name': 'Rule',
                'sequence': 2,
                'ruleset_id': self.ruleset_fixed.id,
                'condition_select': 'none',
                'amount': 30,
            }
        )

    def test_allocation_mode_first(self):
        # let's test evaluation mode
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        self.ruleset_fixed.write({'mode': 'first'})
        self._test_allocation_mode_helper()
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_allocation_mode_min(self):
        # let's test evaluation mode
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        self.ruleset_fixed.write({'mode': 'min'})
        self._test_allocation_mode_helper()
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_allocation_mode_max(self):
        # let's test evaluation mode
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        self.ruleset_fixed.write({'mode': 'max'})
        self._test_allocation_mode_helper()
        self.assertEqual(self.employee.remaining_leaves, 30)

    def test_evaluation_period_anniversary_1(self):
        # let's ensure that anniversary type leave period works well
        self.ruleset_fixed.write({'period': 'anniversary'})
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})

        # employee was hired two years ago
        start_date = date.today() - relativedelta(years=2, days=1)
        self.employee.write({'initial_employment_date': str(start_date)})

        # let's create requests in current period for employee and ensure that
        # employee's allocation reduces
        from_dt = datetime.combine(
            date.today() + relativedelta(days=11), time.min)
        to_dt = datetime.combine(
            date.today() + relativedelta(days=20), time.max)
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': fields.Datetime.to_string(from_dt),
            'date_to': fields.Datetime.to_string(to_dt),
            'number_of_days_temp': 10,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 10)

    def test_evaluation_period_anniversary_2(self):
        # let's ensure that anniversary type leave period works well
        self.ruleset_fixed.write({'period': 'anniversary'})
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})

        # employee was hired two years ago
        start_date = date.today() - relativedelta(years=2, days=1)
        self.employee.write({'initial_employment_date': str(start_date)})
        # let's create requests in a period past and ensure that it does not
        # affect employees allocation
        from_dt = datetime.combine(
            date.today() - relativedelta(days=60), time.min)
        to_dt = datetime.combine(
            date.today() - relativedelta(days=50), time.max)
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': fields.Datetime.to_string(from_dt),
            'date_to': fields.Datetime.to_string(to_dt),
            'number_of_days_temp': 10,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_evaluation_period_anniversary_3(self):
        # let's ensure that anniversary type leave period works well
        self.ruleset_fixed.write({'period': 'anniversary'})
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})

        # employee was hired two years ago
        start_date = date.today() - relativedelta(years=2, days=1)
        self.employee.write({'initial_employment_date': str(start_date)})
        # let's create another in a future period and ensure that it does not
        # affect employee's allocation
        from_dt = datetime.combine(
            date.today() + relativedelta(years=1, days=1), time.min)
        to_dt = datetime.combine(
            date.today() + relativedelta(years=1, days=10), time.max)
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': fields.Datetime.to_string(from_dt),
            'date_to': fields.Datetime.to_string(to_dt),
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_evaluation_period_yearly_1(self):
        # let's ensure that our withdrawal period is handled well
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        year = date.today().year

        # let's create requests in our period
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': '%s-01-02 00:00:01' % (year),
            'date_to': '%s-01-11 23:59:59' % (year),
            'number_of_days_temp': 10,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 10)

    def test_evaluation_period_yearly_2(self):
        # let's ensure that our withdrawal period is handled well
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        year = date.today().year
        # let's create requests in prev period
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': '%s-01-02 00:00:01' % (year - 1),
            'date_to': '%s-01-11 23:59:59' % (year - 1),
            'number_of_days_temp': 10,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_evaluation_period_yearly_3(self):
        # let's ensure that our withdrawal period is handled well
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})
        year = date.today().year
        # let's create requests in next period
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': '%s-01-02 00:00:01' % (year + 1),
            'date_to': '%s-01-11 23:59:59' % (year + 1),
            'number_of_days_temp': 10,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_allocation_in_past(self):
        # let's test that checking allocation in the past works well
        # basically we want to be sure that if we ask the question - what was
        # my allocation x years ago we get an correct response
        self.holiday_status.write({'ruleset_id': self.ruleset_range.id})
        self.employee.write({'initial_employment_date': '2000-10-21'})

        # let's test for various reference dates
        result = self.holiday_status.get_days(
            self.employee.id,
            date(2000, 11, 21)
        )[self.holiday_status.id]['remaining_leaves']
        self.assertEqual(result, 0)

        result = self.holiday_status.get_days(
            self.employee.id,
            date(2001, 11, 21)
        )[self.holiday_status.id]['remaining_leaves']
        self.assertEqual(result, 24)

        # let's ensure that remianing leaves is properly calculated
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': '2001-11-21 00:00:01',
            'date_to': '2001-11-24 23:59:59',
            'number_of_days_temp': 4,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        result = self.holiday_status.get_days(
            self.employee.id,
            date(2001, 11, 25)
        )[self.holiday_status.id]['remaining_leaves']
        self.assertEqual(result, 20)

    def test_allocation_in_future(self):
        # let's test that checking allocation in the future works well
        self.holiday_status.write({'ruleset_id': self.ruleset_range.id})
        self.employee.write({'initial_employment_date': fields.Date.today()})

        dt_ref = date.today() + relativedelta(years=1, days=1)
        result = self.holiday_status.get_days(
            self.employee.id,
            dt_ref
        )[self.holiday_status.id]['remaining_leaves']
        self.assertEqual(result, 24)

        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': datetime.combine(dt_ref, time.min),
            'date_to': datetime.combine(
                dt_ref + relativedelta(days=3), time.max),
            'number_of_days_temp': 4,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        result = self.holiday_status.get_days(
            self.employee.id,
            date(dt_ref.year, 10, 26)
        )[self.holiday_status.id]['remaining_leaves']
        self.assertEqual(result, 20)

    def test_evaluation_virtual(self):
        # let's test our calculation for virtual leaves
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})

        # let's test for various reference dates
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': str(datetime.combine(
                date.today() - relativedelta(days=4), time.min)),
            'date_to': str(datetime.combine(date.today(), time.max)),
            'number_of_days_temp': 4,
        })
        holiday.signal_workflow('confirm')
        result = self.holiday_status.get_days(
            self.employee.id)[self.holiday_status.id]
        self.assertEqual(result['remaining_leaves'], 20)
        self.assertEqual(result['virtual_remaining_leaves'], 16)

        # let's take more than virtual remaining and attest that it fails
        with self.assertRaises(Exception):
            self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_status.id,
                'date_from': str(datetime.combine(
                    date.today() - relativedelta(days=4), time.min)),
                'date_to': str(datetime.combine(date.today(), time.max)),
                'number_of_days_temp': 17,
            })
            for sig in ('confirm', 'validate', 'second_validate'):
                holiday.signal_workflow(sig)

    def test_leave_with_no_limit(self):
        # let's set ruleset just to ensure that it is ignored
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id,
                                   'limit': True})

        # let's test for various reference dates
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': str(datetime.combine(
                date.today() - relativedelta(days=99), time.min)),
            'date_to': str(datetime.combine(date.today(), time.max)),
            'number_of_days_temp': 100,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)
        self.assertEqual(holiday.number_of_days, -100)

    def test_leave_request_over_limit(self):
        # let's test to ensure that code fails if we are asking for too much
        self.holiday_status.write({'ruleset_id': self.ruleset_fixed.id})

        # let's test for various reference dates
        with self.assertRaises(Exception):
            holiday = self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_status.id,
                'date_from': str(datetime.combine(
                    date.today() - relativedelta(days=99), time.min)),
                'date_to': str(datetime.combine(date.today(), time.max)),
                'number_of_days_temp': 100,
            })
            for sig in ('confirm', 'validate', 'second_validate'):
                holiday.signal_workflow(sig)

    def test_evaluation_for_past_period(self):
        # let's test our calculation for vto ensure that if we take a leave in
        # period past it is evaluated against the allocation for that period
        self.holiday_status.write({'ruleset_id': self.ruleset_range.id})

        # employee was hired 5 years ago
        start_date = date.today() - relativedelta(years=5, days=1)
        self.employee.write({'initial_employment_date': str(start_date)})

        # user should have 0 allocation at this time
        with self.assertRaises(Exception):
            holiday = self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_status.id,
                'date_from': str(datetime.combine(start_date, time.min)),
                'date_to': str(datetime.combine(
                    start_date + relativedelta(days=3), time.max)),
                'number_of_days_temp': 4,
            })
            holiday.signal_workflow('confirm')

        # user should have 24 allocation at this time
        with self.assertRaises(Exception):
            holiday = self.holiday_model.create({
                'name': 'Hol10',
                'type': 'remove',
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'holiday_status_id': self.holiday_status.id,
                'date_from': str(datetime.combine(
                    start_date + relativedelta(years=1, days=1), time.min)),
                'date_to': str(datetime.combine(
                    start_date + relativedelta(years=1, days=4), time.max)),
                'number_of_days_temp': 32,
            })
            holiday.signal_workflow('confirm')

    def test_evaluation_for_future_period(self):
        # let's test our calculation for vto ensure that if we take a leave in
        # future periods past it is evaluated against the allocation for that
        # period
        self.holiday_status.write({'ruleset_id': self.ruleset_range.id})

        # employee was hired 5 years ago
        start_date = date.today()
        self.employee.write({'initial_employment_date': str(start_date)})

        # user should have 24 allocation at this time
        holiday = self.holiday_model.create({
            'name': 'Hol10',
            'type': 'remove',
            'holiday_type': 'employee',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_status.id,
            'date_from': str(datetime.combine(
                start_date + relativedelta(years=1, days=1), time.min)),
            'date_to': str(datetime.combine(
                start_date + relativedelta(years=1, days=4), time.max)),
            'number_of_days_temp': 4,
        })
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday.signal_workflow(sig)

        self.assertEquals(holiday.number_of_days, -4.0)
