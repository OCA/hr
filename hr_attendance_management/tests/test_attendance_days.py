# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import fields
from odoo.tests import SavepointCase
import logging

logger = logging.getLogger(__name__)


class TestAttendanceDays(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAttendanceDays, cls).setUpClass()

        cls.gilles = cls.env.ref('hr.employee_qdp')
        cls.pieter = cls.env.ref('hr.employee_root')

        # Add work schedule for Gilles
        cls.gilles.calendar_id = cls.env.ref('resource.timesheet_group1')

        # Create attendance days for employees
        attendances = cls.env['hr.attendance'].search([], order='check_in')
        cls.all_attendances = attendances

    ##########################################################################
    #                           ATTENDANCE DAY                               #
    ##########################################################################

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
        self.assertEqual(p_last_day.rule_id, self.env.ref(
            'hr_attendance_management.break_rule_3'))
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
            else:
                self.assertEqual(p_day.due_hours, 0)
                self.assertEqual(p_day.extra_hours, 0)
        self.assertEqual(pieter_balance, self.pieter.extra_hours)

        # verify that the modifications to an attendance are working
        # get gilles attendances
        gilles_atts = self.env['hr.attendance'].search([
            ('employee_id', '=', self.gilles.id)
        ])
        # get last day and modify its check-in and check-out date
        g_att = gilles_atts[0]

        # initial test value
        self.assertEqual(g_att.worked_hours, 1)

        g_att.write({'check_in': '2018-04-04 08:00:00',
                     'check_out': '2018-04-04 17:00:00'})

        self.assertEqual(g_att.check_in, '2018-04-04 08:00:00')
        self.assertEqual(g_att.check_out, '2018-04-04 17:00:00')
        # worked hours should be computed on the fly
        self.assertEqual(g_att.worked_hours, 9)
        self.assertEqual(g_att.total_attendance, 9)

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
        self.assertEqual(self.gilles.today_hour_formatted, '29:27')

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

    def create_leave_request(self):

        gilles_department_id = self.env['hr.employee'].search([
            ('identification_id', '=', self.gilles.id)
        ]).department_id

        # create leave request for gilles on the day created before
        return self.env['hr.holidays'].create({
            'employee_id': self.gilles.id,
            'department_id': gilles_department_id,
            'date_from': '2018-07-05',
            'date_to': '2018-08-06',
            'holiday_status_id': 4,  # not sure at all it's correct
            'state': 'confirm',
            'type': 'remove',
            'holiday_type': 'employee',
            'keep_due_hours': False
        })

    def test_leave_request(self):
        """ Simply test leave requests """

        self.create_attendance_days_for_leave_request()
        holidays = self.create_leave_request()

        gilles_holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', self.gilles.id),
            ('date_from', '>=', '2018-07-05'),
            ('date_to', '<=', '2018-08-06')
        ])

        g_holi = gilles_holidays[0]
        g_holi._onchange_date_from()

        self.assertEqual(g_holi.number_of_days, -22)
        self.assertEqual(g_holi.holiday_type, 'employee')
        self.assertEqual(g_holi.employee_id.id, self.gilles.id)

        # validates the leave request
        holidays.action_approve()

        # get all gilles's attendance days during his holidays
        gilles_days = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.gilles.id),
            ('date', '>=', '2018-07-05'),
            ('date', '<=', '2018-08-06')
        ])

        # check that due_hours of attendance days during holidays are equal
        # to 0, that they contains a ref to a leave (holiday) and that
        # total_attendance is correctly computed
        for g_day in gilles_days:
            self.assertEqual(g_day.due_hours, 0)
            self.assertEqual(len(g_day.leave_ids), 1)
            g_day._compute_total_attendance()
            self.assertEqual(g_day.total_attendance,
                             g_day.attendance_ids.worked_hours)
