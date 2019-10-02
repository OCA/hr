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

    def test_create_in_surrounding_period(self):
        start_date = datetime.today().replace(year=2019, month=2, day=2)
        end_date = datetime.today().replace(year=2019, month=3, day=3)

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        # TODO more asserts
        self.assertEquals(initial_periods_count + 2, self.get_periods_count(self.jack.id))

        all_periods.unlink()

    def test_create_with_previous_overlapping(self):
        start_date = datetime.today().replace(year=2019, month=5, day=1)
        end_date = datetime.today().replace(year=2019, month=8, day=1)

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        # TODO more asserts
        self.assertEquals(initial_periods_count + 1, self.get_periods_count(self.jack.id))

        all_periods.unlink()

    def test_create_with_previous_non_overlapping(self):
        start_date = datetime.today().replace(year=2019, month=10, day=5)
        end_date = datetime.today().replace(year=2019, month=11, day=1)

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        # TODO more asserts
        self.assertEquals(initial_periods_count + 2, self.get_periods_count(self.jack.id))

        all_periods.unlink()

    def test_create_with_previous_and_next_overlapping(self):
        start_date = datetime.today().replace(year=2018, month=10, day=1)
        end_date = datetime.today().replace(year=2019, month=2, day=1)

        initial_periods_count = self.get_periods_count(self.jack.id)
        self.create_period(start_date, end_date, self.jack.id, True, balance=0, initial_balance=0, lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        # TODO more asserts
        self.assertEquals(initial_periods_count + 1, self.get_periods_count(self.jack.id))

        all_periods.unlink()

    def get_periods_count(self, employee_id):
        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', employee_id)
        ])
        return len(all_periods)

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
