# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo.tests import SavepointCase
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
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

        cls.config = cls.env['base.config.settings'].create({
            'free_break': 0.25,
            'max_extra_hours': 20})
        cls.config.set_free_break()
        cls.config.set_max_extra_hours()
        cls.pieter_leave_request =\
            cls.env.ref('hr_holidays.hr_holidays_employee1_sl')

        # Set recently used attendance days
        last_monday = datetime.now().date() -\
            timedelta(days=datetime.now().weekday()) + timedelta(weeks=-1)

        cls.last_week = [
            last_monday,
            last_monday + timedelta(days=1),
            last_monday + timedelta(days=2),
            last_monday + timedelta(days=3),
            last_monday + timedelta(days=4),
            last_monday + timedelta(days=5),    # saturday
            last_monday + timedelta(days=6),    # sunday
        ]

    ##########################################################################
    #                           ATTENDANCE DAY                               #
    ##########################################################################

    # test create attendance, attendance day and dues_hours
    # test breaks and rules
    # test check_in/check_out
    # test holidays
    # test change day request

# TODO test coefficient

    ##########################################################################
    #                                  CREATE                                #
    ##########################################################################

    def test_create_attendances(self):
        """
        Create an attendance for jack
        check the link between objects and the amount is correct
        """
        date = self.last_week[0]

        # Morning attendance: 3h10
        start_01 = date.strftime('%Y-%m-%d 09:00:00')
        stop_01 = date.strftime('%Y-%m-%d 12:10:00')
        # Afternoon attendance: 5h10
        start_02 = date.strftime('%Y-%m-%d 13:30:00')
        stop_02 = date.strftime('%Y-%m-%d 18:50:00')
        # Amount: 8h20

        attendance_01 = self.env['hr.attendance'].create({
            'check_in': start_01,
            'check_out': stop_01,
            'employee_id': self.jack.id,
        })
        attendance_02 = self.env['hr.attendance'].create({
            'check_in': start_02,
            'check_out': stop_02,
            'employee_id': self.jack.id,
        })

        att_day = self.env['hr.attendance.day'].search(
            [
                ('employee_id', '=', self.jack.id),
                ('id', 'in', [attendance_01.attendance_day_id.id,
                              attendance_02.attendance_day_id.id])
            ])

        # Test that the attendance day has been created and is correctly linked
        self.assertTrue(att_day)
        self.assertEqual(att_day, attendance_01.attendance_day_id)
        self.assertEqual(att_day, attendance_02.attendance_day_id)

        self.assertAlmostEqual(
            att_day.total_attendance,
            attendance_01.worked_hours + attendance_02.worked_hours,
            delta=0.01
        )

    ##########################################################################
    #                            BREAKS / RULES                              #
    ##########################################################################

    def test_breaks_and_rules(self):
        """
        Check the amount of breaks jack and gilles get by the rules.
        """

        def att_8h20_hour_break(employee_id, date):
            """
            Create an attendance of 8h20
            expected rule for demo is 7-9
            """
            # Morning attendance: 3h10
            start_01 = date.strftime('%Y-%m-%d 09:00:00')
            stop_01 = date.strftime('%Y-%m-%d 12:10:00')
            # Afternoon attendance: 5h10
            start_02 = date.strftime('%Y-%m-%d 13:10:00')
            stop_02 = date.strftime('%Y-%m-%d 18:20:00')
            # Amount: 8h20
            # Amount break 1h00

            attendance_01 = self.env['hr.attendance'].create({
                'check_in': start_01,
                'check_out': stop_01,
                'employee_id': employee_id.id,
            })
            attendance_02 = self.env['hr.attendance'].create({
                'check_in': start_02,
                'check_out': stop_02,
                'employee_id': employee_id.id,
            })

            return attendance_01, attendance_02

        def att_10h_no_break(employee_id, date):
            """
            Create an attendance of 10h00
            expected rule for demo is 9-24
            """
            start = date.strftime('%Y-%m-%d 08:00:00')
            stop = date.strftime('%Y-%m-%d 18:00:00')
            attendance = self.env['hr.attendance'].create({
                'check_in': start,
                'check_out': stop,
                'employee_id': employee_id.id,
            })

            return attendance

        # Jack worked 8h20, he took a hour break for lunch
        # Gilles work 10h00, he took no break so the system create one for him

        # Create attendance
        att_jack_01, att_jack_02 =\
            att_8h20_hour_break(self.jack, self.last_week[1])
        att_gilles = att_10h_no_break(self.gilles, self.last_week[1])

        att_day_jack = att_jack_01.attendance_day_id
        att_day_gilles = att_gilles.attendance_day_id

        rule_jack = att_day_jack.rule_id
        rule_gilles = att_day_gilles.rule_id

        # Break rule
        self.assertEqual(rule_jack.name, '7 - 9')
        self.assertEqual(rule_gilles.name, '9 - 24')

        # Breaks
        break_jack = att_day_jack.break_ids.filtered(
            lambda r: not r.is_offered)
        self.assertFalse(break_jack.system_modified)

        break_gilles = att_day_gilles.break_ids.filtered(
            lambda r: not r.is_offered)
        # 0.75 break + 0.25 free break = 1h breaks as 9-24h rule ask
        self.assertEqual(break_gilles.total_duration, 0.75)
        self.assertTrue(break_gilles.system_modified)

        # Duration
        self.assertAlmostEqual(att_jack_01.worked_hours
                               + att_jack_02.worked_hours, 8.33, delta=0.01)
        self.assertAlmostEqual(
            att_day_jack.paid_hours, 8.33, delta=0.01)

        self.assertAlmostEqual(att_gilles.worked_hours, 10.0, delta=0.01)
        self.assertAlmostEqual(att_day_gilles.paid_hours, 9.25, delta=0.01)

        self.assertEqual(att_day_gilles.total_attendance,
                         att_gilles.worked_hours)


    ##########################################################################
    #                        CHECK IN / CHECK OUT                            #
    ##########################################################################


    def test_check_in_check_out(self):
        date = self.last_week[2]
        start = date.strftime('%Y-%m-%d 07:30:00')
        attendance = self.env['hr.attendance'].create({
            'check_in': start,
            'employee_id': self.jack.id,
        })
        att_day = self.env['hr.attendance.day'].search([
            ('employee_id', '=', self.jack.id),
            ('date', '=', attendance.date),
        ])

        ####################################################
        # Test values with no check out
        ####################################################
        self.assertTrue(att_day)
        # The date of attendance_day and attendance are the same as date
        self.assertTrue(
            att_day.date == attendance.date == date.strftime('%Y-%m-%d'))

        # Break rule based on due hours
        self.assertEqual(att_day.rule_id.name, '7 - 9')
        # The free break is created
        self.assertTrue(att_day.break_ids.is_offered is True)

        ####################################################
        # Add the checkout
        ####################################################
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

        self.assertEqual(att_day.rule_id.name, '0 - 5')

    ##########################################################################
    #                              EXTRA HOURS                               #
    ##########################################################################

    def test_max_extra_hours(self):
        """
        Check the rule that limit the number of extra hour

        """
        #            |               michael             |
        #            |  due days  |  amount extra hours  | sum extra hour
        # week 1     |      5     |          20          |   20
        # week 2     |      5     |          20          |   40

        weeks = 2
        date_start = self.last_week[0] - timedelta(weeks=weeks)
        date_stop = self.last_week[0] - timedelta(days=1)

        config = self.env['base.config.settings'].create({})
        config.max_extra_hours = 20
        config.set_max_extra_hours()

        # create 4 week of attendance_day
        self.env['create.hr.attendance.day'].create({
            'date_from': date_start.strftime('%Y-%m-%d'),
            'date_to': date_stop.strftime('%Y-%m-%d'),
            'employee_ids': [(4, self.michael.id), ]
        }).create_attendance_day()

        # create attendance with one extra_hours per day
        extra_hours = 4
        sum_extra_hours = 0
        for att_day in self.michael.attendance_days_ids:
            due_hours = att_day.due_hours

            if due_hours > 0:
                sum_extra_hours += extra_hours

                start = 8   # 8h
                lunch_break = 1
                stop = start + due_hours + lunch_break + extra_hours

                # Morning attendance 8-12
                att_01 = self.env['hr.attendance'].create({
                    'check_in': att_day.date + ' {0:02.0f}:{1:02.0f}:00'
                    .format(*divmod(start * 60, 60)),
                    'check_out': att_day.date + ' 12:00:00',
                    'employee_id': self.michael.id,
                })

                # Afternoon attendance
                att_02 = self.env['hr.attendance'].create({
                    'check_in': att_day.date + ' {0:02.0f}:{1:02.0f}:00'
                    .format(*divmod((12 + lunch_break) * 60, 60)),
                    'check_out': att_day.date + ' {0:02.0f}:{1:02.0f}:00'
                    .format(*divmod(stop * 60, 60)),
                    'employee_id': self.michael.id,
                })
                attendances = att_01 + att_02

                self.assertEqual(att_day.attendance_ids, attendances)
                self.assertEqual(att_day.day_balance, extra_hours)
            else:
                self.assertEquals(att_day.day_balance, 0)

        self.michael.extra_hours_continuous_cap = True
        self.michael.compute_balance()
        self.assertEqual(self.michael.balance, 20)
        self.assertEqual(sum_extra_hours, extra_hours*5*weeks)

    ##########################################################################
    #                             LEAVE REQUEST                              #
    ##########################################################################

    def test_attendance_days_on_leave_request(self):
        """
        Approved leave request of pieter in the odoo demo database
        should be from 20 of the current month to the 22
        We create the attendance days as would do the cron
            _cron_create_attendance

        then we check that the paid hours is correct
        """

        date_format = tools.DEFAULT_SERVER_DATETIME_FORMAT

        leave = self.pieter_leave_request
        date_from = datetime.strptime(leave.date_from, date_format)
        date_to = datetime.strptime(leave.date_to, date_format)

        date_data = [
            (True, date_from + timedelta(days=-1)),
            (False, date_from),
            (False, date_to + timedelta(days=-1)),
            (True, date_to),
        ]

        data = {
            date.strftime('%Y-%m-%d'): (in_leave, date)
            for in_leave, date in date_data
        }

        for date in data.keys():
            self.env['hr.employee'].\
                _cron_create_attendance(
                domain=[('id', '=', self.pieter.id)],
                day=date)

        self.assertNotEqual(leave.attendance_day_ids, None)

        for date, values in data.items():
            att_day = self.pieter.attendance_days_ids.filtered(
                lambda rd: rd.date == date
            )
            self.assertNotEqual(att_day, None)

            if values[0]:
                if att_day.due_hours != 0:
                    self.assertNotEqual(att_day.paid_hours, att_day.due_hours)
            else:
                self.assertEqual(att_day.paid_hours, att_day.due_hours)

                # leave
                self.assertEqual(leave in att_day.leave_ids, True)

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
