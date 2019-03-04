# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo import fields
from odoo.tests import SavepointCase
import logging

logger = logging.getLogger(__name__)


class TestAttendanceDays(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAttendanceDays, cls).setUpClass()

        cls.jack = cls.env.ref('hr.employee_fme')
        cls.gilles = cls.env.ref('hr.employee_qdp')
        cls.pieter = cls.env.ref('hr.employee_root')
        cls.michael = cls.env.ref('hr.employee_niv')

        # Add work schedule (8h/work days) for Gilles, Jack and Michael
        cls.gilles.calendar_id = cls.env.ref('resource.timesheet_group1')
        cls.jack.calendar_id = cls.env.ref('resource.timesheet_group1')
        cls.michael.calendar_id = cls.env.ref('resource.timesheet_group1')

        # Set free break
        cls.env['ir.config_parameter'].set_param(
            'hr_attendance_management.free_break', '0.25')
        cls.env['ir.config_parameter'].set_param(
            'hr_attendance_management.max_extra_hours', '20')

        # Create attendance days for employees
        attendances = cls.env['hr.attendance'].search([], order='check_in')
        cls.all_attendances = attendances

    ##########################################################################
    #                           ATTENDANCE DAY                               #
    ##########################################################################
    def test_attendance_day(self):
        monday = (datetime.now().date()
                  - timedelta(days=datetime.now().weekday())
                  + timedelta(weeks=-1))
        tuesday = monday + timedelta(days=1)

        self.create_first_attendance(monday)

        self.add_attendance_no_check_out(tuesday)
        self.attendance_check_out(tuesday)
        self.add_second_attendance(tuesday)
        self.add_third_attendance(tuesday)

    def test_max_extra_hours(self):
        date_stop = (datetime.now().date())
        date_start = date_stop - timedelta(weeks=4)

        self.env['ir.config_parameter'].set_param(
            'hr_attendance_management.max_extra_hours', '20')

        # create attendance_day
        self.env['create.hr.attendance.day'].create({
            'date_from': date_start.strftime('%Y-%m-%d'),
            'date_to': date_stop.strftime('%Y-%m-%d'),
            'employee_ids': [(4, self.michael.id), ]
        }).create_attendance_day()

        # create attendance with one extra_hours per day
        sum_extra_hours = 0
        for att_day in self.michael.attendance_days_ids:
            sum_extra_hours += 1

            due_hours = att_day.due_hours
            due_break = att_day.due_break_total
            free_break = att_day.free_breaks_hours

            start = 7
            stop = start + due_hours + due_break - free_break + 1
            attendance = self.env['hr.attendance'].create({
                'check_in': att_day.date + ' {num:02d}:00'.format(num=start),
                'check_out': att_day.date + ' {0:02.0f}:{1:02.0f}'.format(
                    *divmod(stop * 60, 60)),
                'employee_id': self.michael.id,
            })

            self.assertEqual(att_day.attendance_ids, attendance)
            self.assertEqual(att_day.extra_hours, 1)

        self.assertEqual(self.michael.extra_hours, 20)

    def create_first_attendance(self, date):
        """
        Create an attendance for last friday from 09:00 to 18:20 for a
        duration of 9 hours and 20 minutes. A break of 30 minutes is created by
        the system, thereby the paid hours should be 8 hours and 50 minutes and
        the rule break 7-9.
        :return: None
        """

        start = date.strftime('%Y-%m-%d 09:00')
        stop = date.strftime('%Y-%m-%d 18:20')
        attendance = self.env['hr.attendance'].create({
            'check_in': start,
            'check_out': stop,
            'employee_id': self.jack.id,
        })

        att_day = self.env['hr.attendance.day'].search(
            [('employee_id', '=', self.jack.id)])

        # Test that the attendance day has been created
        self.assertTrue(att_day)
        self.assertEqual(att_day, attendance.attendance_day_id)

        # Break rule
        self.assertEqual(att_day.rule_id.name, '7 - 9')

        # Breaks
        created_break = att_day.break_ids.filtered(lambda r: not r.is_offered)
        self.assertEqual(created_break.total_duration, 0.5)
        self.assertTrue(created_break.system_modified)

        # Duration
        self.assertAlmostEqual(attendance.worked_hours, 9.33, delta=0.01)
        self.assertAlmostEqual(att_day.paid_hours, 8.83, delta=0.01)

        # Explicit!
        self.assertEqual(att_day.total_attendance, attendance.worked_hours)

        # The free break + this one create by the system = 2 breaks
        self.assertEqual(len(att_day.break_ids), 2)

    def add_attendance_no_check_out(self, date):
        start = date.strftime('%Y-%m-%d 07:30')
        attendance = self.env['hr.attendance'].create({
            'check_in': start,
            'employee_id': self.jack.id,
        })
        att_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.jack.id),
            ('date', '=', attendance.date),
        ])

        # Test that the attendance day has been created
        self.assertTrue(att_day)

        # The date of attendance_day and attendance are the same as date
        self.assertTrue(
            att_day.date == attendance.date == date.strftime('%Y-%m-%d'))

        # The free break is created
        self.assertTrue(att_day.break_ids.is_offered is True)

        # Break rule based on due hours
        self.assertEqual(att_day.rule_id.name, '7 - 9')

    def attendance_check_out(self, date):
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.jack.id),
            ('date', '=', date.strftime('%Y-%m-%d')),
        ]).filtered(
            lambda r: not r.check_out)
        attendance.check_out = date.strftime('%Y-%m-%d 12:00:00')

        att_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.jack.id),
            ('date', '=', attendance.date),
        ])

        # Check duration
        self.assertEqual(attendance.total_attendance, 4.5)
        self.assertEqual(att_day.paid_hours, 4.5)

    def add_second_attendance(self, date):
        start = date.strftime('%Y-%m-%d 13:30')
        stop = date.strftime('%Y-%m-%d 17:00')
        attendance = self.env['hr.attendance'].create({
            'check_in': start,
            'check_out': stop,
            'employee_id': self.jack.id,
        })
        att_day = attendance.attendance_day_id

        self.assertEqual(att_day.total_attendance, 8.0)
        self.assertEqual(att_day.break_total, 1.75)
        self.assertEqual(len(att_day.break_ids), 2)

    def add_third_attendance(self, date):
        start = date.strftime('%Y-%m-%d 19:30')
        stop = date.strftime('%Y-%m-%d 21:00')
        attendance = self.env['hr.attendance'].create({
            'check_in': start,
            'check_out': stop,
            'employee_id': self.jack.id,
        })
        att_day = attendance.attendance_day_id

        self.assertEqual(att_day.total_attendance, 9.5)
        self.assertEqual(att_day.break_total, 4.25)
        self.assertEqual(len(att_day.break_ids), 3)

        for a_break in att_day.break_ids.filtered(lambda r: not r.is_offered):
            self.assertEqual(a_break.system_modified, False)

    def create_attendance_days(self):
        # for attendance day testing
        attendances = self.all_attendances
        date_start = attendances[0].check_in
        date_stop = attendances[-1].check_out
        self.env['create.hr.attendance.day'].create({
            'date_from': date_start[:10],
            'date_to': date_stop[:10],
            'employee_ids': [(4, self.gilles.id), (4, self.pieter.id)]
        }).create_attendance_day()

        # for today hour formatting
        self.env['create.hr.attendance.day'].create({
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today(),
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

        # for due_hour modification with a write() on forced_due_hours
        self.env['create.hr.attendance.day'].create({
            'date_from': '2020-04-04 08:00:00',
            'date_to': '2020-04-04 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

    def test_normal_case(self):
        """ Simply test attendance are correctly created. """
        self.create_attendance_days()
        day_obj = self.env['hr.attendance.day']

        pieter_days = day_obj.search([
            ('employee_id', '=', self.pieter.id),
            ('date', '<', fields.Date.today())
        ], order='date desc')
        # Pieter is admin and has only one day logged day, yesterday.
        p_last_day = pieter_days[0]
        # Bunch of tests for the attendance day
        self.assertTrue(p_last_day)
        self.assertEqual(len(p_last_day.attendance_ids), 2)
        self.assertEqual(p_last_day.total_attendance, 9)
        self.assertEqual(p_last_day.paid_hours, 9)
        self.assertEqual(p_last_day.extra_hours_lost, 0)
        self.assertEqual(p_last_day.due_break_min, 0.5)
        self.assertEqual(p_last_day.due_break_total, 1)
        self.assertEqual(len(p_last_day.break_ids), 1)
        self.assertEqual(p_last_day.break_total, 1)
        self.assertEqual(p_last_day.rule_id.name, '9 - 24')
        p_date = fields.Date.from_string(p_last_day.date)
        if p_date.weekday() <= 4:
            self.assertEqual(p_last_day.due_hours, 8)
            self.assertEqual(p_last_day.extra_hours, 1)
        else:
            self.assertEqual(p_last_day.due_hours, 0)
            self.assertEqual(p_last_day.extra_hours, 9)
        # Another Pieter day would count as negative extra hours, except
        # the weekend and leave days.
        pieter_balance = p_last_day.extra_hours
        for p_day in pieter_days[1:]:
            p_date = fields.Date.from_string(p_day.date)
            pieter_balance += p_day.extra_hours
            if p_date.weekday() <= 4 and not p_day.leave_ids.filtered(
                    lambda l: l.state == 'validate'):
                self.assertEqual(p_day.due_hours, 8)
                self.assertEqual(p_day.extra_hours, -8)
        self.assertEqual(pieter_balance, self.pieter.extra_hours)

        # test annual balance computation
        self.assertEqual(self.gilles.annual_balance, 0)
        g_previous_balance = self.gilles.previous_annual_balance
        g_extra_hours = self.gilles.extra_hours
        self.gilles._cron_compute_annual_balance()
        self.assertEqual(self.gilles.annual_balance, g_previous_balance
                         + g_extra_hours)

        # test formatting of today hour
        self.gilles._compute_today_hour()
        self.gilles._compute_today_hour_formatted()
        self.assertEqual(self.gilles.today_hour_formatted,
                         '{:02d}:{:02d}'.format(*divmod(int(abs(float(
                             self.gilles.calc_today_hour()) * 60)), 60)))

        # test modification of due_hours with a write() on forced_due_hours
        forced_due_hours = self.env['hr.forced.due.hours'].create({
            'employee_id': self.gilles.id,
            'date': '2020-04-04',
            'forced_due_hours': 9
        })
        forced_due_hours.write({
            'employee_id': self.gilles.id,
            'date': '2020-04-04',
            'forced_due_hours': 6
        })
        g_day_changed_due_hours = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.gilles.id),
            ('date', '=', '2020-04-04')
        ])[0]
        self.assertEqual(g_day_changed_due_hours.due_hours, 6)

    ##########################################################################
    #                         CHANGE DAY REQUEST                             #
    ##########################################################################

    def create_change_day_request(self):
        # create change request for attendance day previously created
        self.env['hr.change.day.request'].create({
            'employee_id': self.gilles.id,
            'date1': '2018-07-05',
            'date2': '2018-08-02',
            'forced1': 0,
            'forced2': 5
        })

    def create_attendance_days_for_change_day_request(self):

        # create attendance day for gilles
        self.env['create.hr.attendance.day'].create({
            'date_from': '2018-07-05 08:00:00',
            'date_to': '2018-07-05 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

        # create new attendance day for gilles
        self.env['create.hr.attendance.day'].create({
            'date_from': '2018-08-02 08:00:00',
            'date_to': '2018-08-02 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

    def test_change_day_request(self):
        """ Simply test change day requests """

        self.create_attendance_days_for_change_day_request()

        gilles_old_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.gilles.id),
            ('date', '=', '2018-07-05')
        ])

        self.assertEqual(gilles_old_day.due_hours, 8)
        self.create_change_day_request()

        gilles_new_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.gilles.id),
            ('date', '=', '2018-08-02')
        ])

        self.assertEqual(gilles_old_day.due_hours, 0)
        self.assertEqual(gilles_new_day.due_hours, 5)

    ##########################################################################
    #                             LEAVE REQUEST                              #
    ##########################################################################

    def create_attendance_days_for_leave_request(self):
        # create attendance days for gilles

        # first day of vacation
        self.env['create.hr.attendance.day'].create({
            'date_from': '2018-07-05 08:00:00',
            'date_to': '2018-07-05 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

        # day in the middle of vacation
        self.env['create.hr.attendance.day'].create({
            'date_from': '2018-07-10 08:00:00',
            'date_to': '2018-07-10 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()

        # last day of vacation
        self.env['create.hr.attendance.day'].create({
            'date_from': '2018-08-06 08:00:00',
            'date_to': '2018-08-06 17:00:00',
            'employee_ids': [(4, self.gilles.id)]
        }).create_attendance_day()
