# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.tests import SavepointCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
import logging

logger = logging.getLogger(__name__)


class TestPeriod(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPeriod, cls).setUpClass()

        cls.jack = cls.env.ref('hr.employee_fme')

        cls.start_date_1 = datetime.today().replace(year=2018, month=1, day=1)
        cls.end_date_1 = datetime.today().replace(year=2018, month=6, day=1)

        cls.start_date_2 = datetime.today().replace(year=2018, month=6, day=7)
        cls.end_date_2 = datetime.today().replace(year=2018, month=12, day=31)

        cls.start_date_3 = datetime.today().replace(year=2019, month=1, day=1)
        cls.end_date_3 = datetime.today().replace(year=2019, month=6, day=1)

        cls.env['hr.employee.period'].search([
            ('employee_id', '=', cls.jack.id)
        ]).unlink()

        cls.period1 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_1,
            'end_date': cls.end_date_1,
            'balance': 0,
            'previous_balance': 0,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "override"
        })

        cls.period2 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_2,
            'end_date': cls.end_date_2,
            'balance': 0,
            'previous_balance': 0,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "override"
        })

        cls.period3 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_3,
            'end_date': cls.end_date_3,
            'balance': 0,
            'previous_balance': 0,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "override"
        })

    # Add a period "inside" another one. 1 more periods should be created (after) and 1 should be modified
    def test_create_in_surrounding_period(self):
        start_date = datetime.today().replace(year=2019, month=2, day=2)
        end_date = datetime.today().replace(year=2019, month=3, day=3)

        old_surrounding_period = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id),
            ('start_date', '<', start_date)
        ], order='start_date desc', limit=1)
        old_surrounding_start_date = old_surrounding_period.start_date
        old_surrounding_end_date = old_surrounding_period.end_date

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 2, self.get_periods_count(self.jack.id))

        previous_period = self.get_previous_period(start_date, self.jack.id)
        next_period = self.get_next_period(end_date, self.jack.id)
        self.assertEquals(datetime.strptime(previous_period.end_date, '%Y-%m-%d').date(),
                          (start_date - timedelta(days=1)).date())
        self.assertEquals(old_surrounding_start_date, previous_period.start_date)
        self.assertEquals(next_period.end_date, old_surrounding_end_date)
        self.assertEquals(datetime.strptime(next_period.start_date, '%Y-%m-%d').date(),
                          (end_date + timedelta(days=1)).date())

        all_periods.unlink()

    # Add a period with the previous one finishing in the bounds of the new one.
    # The previous overlapping should be modified
    def test_create_with_previous_overlapping(self):
        start_date = datetime.today().replace(year=2019, month=5, day=1)
        end_date = datetime.today().replace(year=2019, month=8, day=1)

        old_previous_overlapping = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id),
            ('end_date', '>', start_date),
            ('end_date', '<', end_date),
            ('start_date', '<', start_date)
        ], order='end_date desc', limit=1)
        old_previous_overlapping_start_date = old_previous_overlapping.start_date

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 1, self.get_periods_count(self.jack.id))

        previous_period = self.get_previous_period(start_date, self.jack.id)
        self.assertEquals(datetime.strptime(previous_period.end_date, '%Y-%m-%d').date(),
                          (start_date - timedelta(days=1)).date())
        self.assertEquals(old_previous_overlapping_start_date, previous_period.start_date)

        next_period = self.get_next_period(end_date, self.jack.id)
        self.assertFalse(next_period)

        all_periods.unlink()

    # Add a period more than 1 day after the last one.
    # 1 more period should be added between the last one and the new one
    def test_create_with_previous_non_overlapping(self):
        start_date = datetime.today().replace(year=2019, month=10, day=5)
        end_date = datetime.today().replace(year=2019, month=11, day=1)

        old_previous_period = self.get_previous_period(start_date, self.jack.id)
        old_previous_start_date = old_previous_period.start_date
        old_previous_end_date = old_previous_period.end_date

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 2, self.get_periods_count(self.jack.id))

        new_previous_period = self.get_previous_period(start_date, self.jack.id)
        self.assertEquals((datetime.strptime(old_previous_end_date, '%Y-%m-%d') + timedelta(days=1)).date(),
                          datetime.strptime(new_previous_period.start_date, '%Y-%m-%d').date())
        self.assertEquals(datetime.strptime(new_previous_period.end_date, '%Y-%m-%d').date(),
                          (start_date - timedelta(days=1)).date())

        all_periods.unlink()

    # Add a period with the previous one finishing in the bounds of the new one and
    # the next one also beginning in the bounds of the new one. The 2 overlapping periods should be modified
    def test_create_with_previous_and_next_overlapping(self):
        start_date = datetime.today().replace(year=2018, month=10, day=1)
        end_date = datetime.today().replace(year=2019, month=2, day=1)

        old_previous_overlapping = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id),
            ('end_date', '>', start_date),
            ('end_date', '<', end_date),
            ('start_date', '<', start_date)
        ], order='end_date desc', limit=1)
        old_previous_overlapping_start_date = old_previous_overlapping.start_date

        old_next_overlapping = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id),
            ('end_date', '>', end_date),
            ('start_date', '<', end_date),
            ('start_date', '>', start_date)
        ], order='start_date asc', limit=1)
        old_next_overlapping_end_date = old_next_overlapping.end_date

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 1, self.get_periods_count(self.jack.id))

        new_previous_period = self.get_previous_period(start_date, self.jack.id)
        new_next_period = self.get_next_period(end_date, self.jack.id)
        self.assertEquals(new_previous_period.start_date, old_previous_overlapping_start_date)
        self.assertEquals(datetime.strptime(new_previous_period.end_date, '%Y-%m-%d').date(),
                          (start_date - timedelta(days=1)).date())
        self.assertEquals(datetime.strptime(new_next_period.start_date, '%Y-%m-%d').date(),
                          (end_date + timedelta(days=1)).date())
        self.assertEquals(new_next_period.end_date, old_next_overlapping_end_date)

        all_periods.unlink()

    def get_periods_count(self, employee_id):
        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', employee_id)
        ])
        return len(all_periods)

    def get_next_period(self, end_date, employee_id):
        return self.env['hr.employee.period'].search([
            ('employee_id', '=', employee_id),
            ('start_date', '>', end_date)
        ], order='start_date asc', limit=1)

    def get_previous_period(self, start_date, employee_id):
        return self.env['hr.employee.period'].search([
            ('employee_id', '=', employee_id),
            ('end_date', '<', start_date)
        ], order='end_date desc', limit=1)

    def create_period(self, start_date, end_date, employee_id, continuous_cap, balance, initial_balance, lost):
        self.env['hr.employee.period'].create({
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_balance': initial_balance,
            'lost': lost,
            'employee_id': employee_id,
            'continuous_cap': continuous_cap,
        })
