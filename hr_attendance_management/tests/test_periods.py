# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from datetime import datetime, timedelta
from odoo.tests import SavepointCase
import logging

logger = logging.getLogger(__name__)


class TestPeriod(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPeriod, cls).setUpClass()

        cls.jack = cls.env.ref('hr.employee_fme')
        cls.gilles = cls.env.ref('hr.employee_qdp')
        cls.gilles.calendar_id = 1
        cls.gilles.initial_balance = 0

        cls.start_date_1 = datetime.today().replace(year=2018, month=1, day=1)
        cls.end_date_1 = datetime.today().replace(year=2018, month=5, day=31)

        cls.start_date_2 = datetime.today().replace(year=2018, month=6, day=1)
        cls.end_date_2 = datetime.today().replace(year=2018, month=12, day=31)

        cls.start_date_3 = datetime.today().replace(year=2019, month=1, day=1)
        cls.end_date_3 = datetime.today().replace(year=2019, month=6, day=1)

        cls.env['hr.employee.period'].search([
            ('employee_id', '=', cls.jack.id)
        ]).unlink()

        cls.period1 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_1,
            'end_date': cls.end_date_1,
            'balance': 1,
            'previous_period': None,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "create"
        })

        cls.period2 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_2,
            'end_date': cls.end_date_2,
            'balance': 2,
            'previous_period': cls.period1.id,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "create"
        })

        cls.period3 = cls.env['hr.employee.period'].create({
            'start_date': cls.start_date_3,
            'end_date': cls.end_date_3,
            'balance': 3,
            'previous_period': cls.period2.id,
            'lost': 0,
            'employee_id': cls.jack.id,
            'continuous_cap': True,
            'origin': "create"
        })

    def create_att_day_for_date_with_supp_hours(self, date, employee_id, hours=0):
        start_01 = date.replace(hour=8, minute=0, second=0)
        stop_01 = date.replace(hour=12, minute=0, second=0)
        # 4h in the morning
        start_02 = date.replace(hour=12, minute=30, second=0)
        stop_02 = date.replace(hour=16+hours, minute=30, second=0)
        # 4h + hours in the afternoon

        self.env['hr.attendance'].create({
            'check_in': start_01,
            'check_out': stop_01,
            'employee_id': employee_id,
        })
        self.env['hr.attendance'].create({
            'check_in': start_02,
            'check_out': stop_02,
            'employee_id': employee_id,
        })

    def add_hours_to_last_attendance_day(self, hours, employee_id):
        last_att_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', employee_id)
        ], order="date asc")[-1]

        last_attendance = \
            last_att_day.attendance_ids.sorted(
                key=lambda a: a.date and a.check_out)[-1]

        last_attendance.write({
            'check_out': fields.Datetime.from_string(last_attendance.check_out) +
            timedelta(hours=hours)
        })

    def test_changing_att_day_balance(self):
        self.gilles.period_ids.unlink()
        # 01.01.2018
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_1, self.gilles.id, 1)
        # 01.06.2018
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_2, self.gilles.id, 1)
        # 01.01.2019
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_3, self.gilles.id, 1)

        # self.assertEquals(self.gilles.balance, 0)
        self.gilles.compute_balance(store=True)
        self.assertEquals(len(self.gilles.period_ids), 1)
        self.assertEquals(self.gilles.period_ids[0].final_balance, 3)
        self.assertEquals(self.gilles.balance, 3)

        self.add_hours_to_last_attendance_day(1, self.gilles.id)
        self.gilles.compute_balance()
        self.assertEquals(self.gilles.balance, 4)
        self.assertEquals(self.gilles.period_ids[0].final_balance, 4)

    def test_period_balances(self):
        self.gilles.period_ids.unlink()
        # 01.01.2018
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_1, self.gilles.id, 1)
        # 01.06.2018
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_2, self.gilles.id, 1)
        # 01.01.2019
        self.create_att_day_for_date_with_supp_hours(
            self.start_date_3, self.gilles.id, 1)

        att_days = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.gilles.id)
        ])
        self.assertEquals(len(att_days), 3)

        # compute balance and store the period calculated
        self.gilles.compute_balance(store=True)
        self.assertEquals(len(self.gilles.period_ids), 1)
        self.assertEquals(self.gilles.period_ids[0].final_balance, 3)
        self.assertEquals(self.gilles.balance, 3)

        start_date = datetime.today().replace(year=2019, month=1, day=1)
        end_date = datetime.today()
        # Create new period beginning in 01.01.2019,
        # 1 more period should be created before
        new_period = self.create_period(start_date,
                                        end_date,
                                        self.gilles.id,
                                        False,
                                        0,
                                        None,
                                        0)
        self.assertEquals(new_period.balance, 1)
        self.assertEquals(new_period.final_balance, 3)
        self.assertEquals(len(self.gilles.period_ids), 2)
        auto_created_period = \
            self.gilles.period_ids.sorted(key=lambda p: p.start_date)[0]
        self.assertEquals(auto_created_period.balance, 2)
        self.assertEquals(auto_created_period.final_balance, 3)
        self.gilles.period_ids.unlink()

        # Create a period for 2018
        new_period_2 = self.create_period(start_date.replace(year=2018),
                                          end_date.replace(year=2019, month=1, day=1),
                                          self.gilles.id,
                                          False,
                                          0,
                                          None,
                                          0)
        self.assertEquals(len(self.gilles.period_ids), 1)
        self.assertEquals(new_period_2.balance, 2)
        self.assertEquals(new_period_2.final_balance, 2)
        # create a period for second half of 2019, 1 period should be auto created
        new_period_3 = self.create_period(start_date.replace(
                                              year=2019, month=6, day=1),
                                          end_date.replace(
                                              year=2019, month=12, day=31),
                                          self.gilles.id,
                                          False,
                                          0,
                                          None,
                                          0)
        self.assertEquals(len(self.gilles.period_ids), 3)
        self.assertEquals(new_period_3.balance, 0)
        self.assertEquals(new_period_3.final_balance, 3)
        auto_created_period = \
            self.gilles.period_ids.sorted(key=lambda p: p.start_date)[1]
        self.assertEquals(auto_created_period.balance, 1)
        self.assertEquals(self.gilles.balance, 3)

        # existing periods should be modified to make place for the new one
        new_period_4 = self.create_period(start_date.replace(
                                              year=2018, month=7, day=1),
                                          end_date.replace(
                                              year=2019, month=2, day=1),
                                          self.gilles.id,
                                          False,
                                          0,
                                          None,
                                          0)
        self.assertEquals(len(self.gilles.period_ids), 4)
        self.assertEquals(new_period_4.balance, 1)
        self.assertEquals(new_period_4.final_balance, 3)

        self.gilles.initial_balance = 1
        self.assertEquals(new_period_4.final_balance, 4)
        self.assertEquals(self.gilles.balance, 4)

    # Add a period "inside" another one.
    # 1 more periods should be created (after) and 1 should be modified
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
        self.create_period(start_date,
                           end_date,
                           self.jack.id,
                           True,
                           balance=0,
                           previous_period=None,
                           lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 2,
                          self.get_periods_count(self.jack.id))

        previous_period = self.get_previous_period(start_date, self.jack.id)
        next_period = self.get_next_period(end_date, self.jack.id)
        self.assertEquals(
            datetime.strptime(previous_period.end_date, '%Y-%m-%d').date(),
            start_date.date()
        )
        self.assertEquals(old_surrounding_start_date, previous_period.start_date)
        self.assertEquals(next_period.end_date, old_surrounding_end_date)
        self.assertEquals(datetime.strptime(next_period.start_date, '%Y-%m-%d').date(),
                          end_date.date())

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
        self.create_period(start_date,
                           end_date,
                           self.jack.id,
                           True,
                           balance=0,
                           previous_period=None,
                           lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 1,
                          self.get_periods_count(self.jack.id))

        previous_period = self.get_previous_period(start_date, self.jack.id)
        self.assertEquals(
            datetime.strptime(previous_period.end_date, '%Y-%m-%d').date(),
            start_date.date()
        )
        self.assertEquals(old_previous_overlapping_start_date,
                          previous_period.start_date)

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
        self.create_period(start_date,
                           end_date,
                           self.jack.id,
                           True,
                           balance=0,
                           previous_period=None,
                           lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 2,
                          self.get_periods_count(self.jack.id))

        new_previous_period = self.get_previous_period(start_date, self.jack.id)
        self.assertEquals(
            datetime.strptime(old_previous_end_date, '%Y-%m-%d').date(),
            datetime.strptime(new_previous_period.start_date, '%Y-%m-%d').date()
        )
        self.assertEquals(
            datetime.strptime(new_previous_period.end_date, '%Y-%m-%d').date(),
            start_date.date()
        )

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
        self.create_period(start_date,
                           end_date,
                           self.jack.id,
                           True,
                           balance=0,
                           previous_period=None,
                           lost=0)

        all_periods = self.env['hr.employee.period'].search([
            ('employee_id', '=', self.jack.id)
        ])
        self.assertEquals(initial_periods_count + 1,
                          self.get_periods_count(self.jack.id))

        new_previous_period = self.get_previous_period(start_date, self.jack.id)
        new_next_period = self.get_next_period(end_date, self.jack.id)
        self.assertEquals(new_previous_period.start_date,
                          old_previous_overlapping_start_date)
        self.assertEquals(
            datetime.strptime(new_previous_period.end_date, '%Y-%m-%d').date(),
            start_date.date()
        )
        self.assertEquals(
            datetime.strptime(new_next_period.start_date, '%Y-%m-%d').date(),
            end_date.date()
        )
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
            ('start_date', '>=', end_date)
        ], order='start_date asc', limit=1)

    def get_previous_period(self, start_date, employee_id):
        return self.env['hr.employee.period'].search([
            ('employee_id', '=', employee_id),
            ('end_date', '<=', start_date)
        ], order='end_date desc', limit=1)

    def create_period(self, start_date, end_date, employee_id, continuous_cap,
                      balance, previous_period, lost):
        return self.env['hr.employee.period'].create({
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_period': previous_period,
            'lost': lost,
            'employee_id': employee_id,
            'continuous_cap': continuous_cap,
        })
