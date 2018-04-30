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

    def create_attendance_days(self):
        attendances = self.all_attendances
        date_start = attendances[0].check_in
        date_stop = attendances[-1].check_out
        self.env['create.hr.attendance.day'].create({
            'date_from': date_start[:10],
            'date_to': date_stop[:10],
            'employee_ids': [(4, self.gilles.id), (4, self.pieter.id)]
        }).create_attendance_day()

    def test_normal_case(self):
        """ Simply test attendance are correctly created. """
        self.create_attendance_days()
        day_obj = self.env['hr.attendance.day']
        # gilles_days = day_obj.search([
        #     ('employee_id', '=', self.gilles.id)
        # ])
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

        # TODO test creating and changing attendances

    def test_change_day_request(self):
        # TODO Implement
        pass

    def test_leave_request(self):
        # TODO Implement
        pass
