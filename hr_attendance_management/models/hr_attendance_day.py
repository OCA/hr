# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import pytz

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrAttendanceDay(models.Model):
    """
    The instances of hr.attendance.day is created either at the first
    attendance of the day or by the method
    hr.employee._cron_create_attendance() called by a cron everyday.
    """
    _name = "hr.attendance.day"
    _description = "Attendance day"
    _order = 'date DESC'
    _sql_constraints = [('unique_attendance_day', 'unique(date, employee_id)',
                         'This "Attendance day" already exists for this '
                         'employee')]

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    date = fields.Date(required=True, default=fields.Date.today())
    employee_id = fields.Many2one(
        'hr.employee', "Employee", ondelete="cascade", required=True,
        default=lambda self: self.env.user.employee_ids[0].id)

    # Working schedule
    working_schedule_id = fields.Many2one('resource.calendar', store=True,
                                          string='Working schedule',
                                          compute='_compute_working_schedule',
                                          inverse='_inverse_working_schedule')
    cal_att_ids = fields.Many2many('resource.calendar.attendance', store=True,
                                   compute='_compute_cal_att_ids')
    working_day = fields.Char(compute='_compute_working_day',
                              readonly=True, store=True)
    name = fields.Char(compute='_compute_name', store=True)

    # Leaves
    leave_ids = fields.Many2many('hr.holidays', string='Leaves')
    # todo replace by employee_id.is_absent_totay
    in_leave = fields.Boolean('In leave', compute='_compute_in_leave',
                              store=True)
    public_holiday_id = fields.Many2one('hr.holidays.public.line',
                                        'Public holidays')

    # Due hours
    due_hours = fields.Float('Due hours', compute='_compute_due_hours',
                             readonly=True, store=True)

    # Attendances
    attendance_ids = fields.One2many('hr.attendance', 'attendance_day_id',
                                     'Attendances', readonly=True)

    has_change_day_request = fields.Boolean(
        compute='_compute_has_change_day_request', store=True,
        oldname='has_linked_change_day_request'
    )

    # Worked
    paid_hours = fields.Float(
        compute='_compute_paid_hours', store=True, readonly=True
    )
    free_breaks_hours = fields.Float(compute='_compute_free_break_hours')
    total_attendance = fields.Float(
        compute='_compute_total_attendance', store=True,
        help='Sum of all attendances of the day'
    )

    coefficient = fields.Float(help='Worked hours coefficient')

    # Break
    due_break_min = fields.Float('Minimum break due',
                                 compute='_compute_due_break')
    due_break_total = fields.Float('Total break due',
                                   compute='_compute_due_break')
    break_ids = fields.One2many('hr.attendance.break',
                                'attendance_day_id',
                                'Breaks',
                                readonly=True)
    break_total = fields.Float('Total break',
                               compute='_compute_break_total',
                               store=True)
    rule_id = fields.Many2one('hr.attendance.rules', 'Rules',
                              compute='_compute_rule_id')

    # Extra hours
    extra_hours = fields.Float("Extra hours",
                               compute='_compute_extra_hours',
                               store=True)
    extra_hours_lost = fields.Float(readonly=True)

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    @api.multi
    @api.depends('attendance_ids')
    def _compute_working_schedule(self):
        for att_day in self:
            # Find the correspondent resource.calendar
            # First check if the attendance has already a resource.calendar
            schedule = att_day.attendance_ids.mapped('working_schedule_id')
            if schedule:
                # if there is more than one resource.calendar take one...
                schedule = schedule[0]
            else:
                # look for a valid contract...
                # todo: check if att_day.employee_id.current_contract is enough
                contracts = self.env['hr.contract'].search([
                    ('employee_id', '=', att_day.employee_id.id),
                    ('date_start', '<=', att_day.date),
                    '|', ('date_end', '=', False),
                    ('date_end', '>=', att_day.date)
                ], order='date_start desc', limit=1)
                # ...or take the resource.calendar of employee
                schedule = contracts.working_hours or (
                    att_day.employee_id.calendar_id)

            att_day.working_schedule_id = schedule

    def _inverse_working_schedule(self):
        for att_day in self:
            for att in self.attendance_ids:
                att.working_schedule_id = att_day.working_schedule_id

    @api.multi
    @api.depends('working_schedule_id', 'working_schedule_id.attendance_ids')
    def _compute_cal_att_ids(self):
        """
        Find the resource.calendar.attendance matching
        """
        for att_day in self:
            week_day = fields.Date.from_string(att_day.date).weekday()

            # select the calendar attendance(s) that are valid today.
            current_cal_att = att_day.working_schedule_id.mapped(
                'attendance_ids').filtered(
                lambda a: int(a.dayofweek) == week_day)

            # Specific period
            att_schedule = current_cal_att.filtered(
                lambda r: r.date_from is not False and
                r.date_to is not False and
                r.date_from <= att_day.date <= r.date_to)

            # Period with only date_to or date_from
            if not att_schedule:
                att_schedule = current_cal_att.filtered(
                    lambda r: (r.date_from <= att_day.date and
                               not r.date_to and r.date_from) or
                              (r.date_to >= att_day.date and
                               not r.date_from and r.date_to))

            # Default schedule
            if not att_schedule:
                att_schedule = current_cal_att.filtered(
                    lambda r: not r.date_from and not r.date_to)

            att_day.cal_att_ids = att_schedule

    @api.multi
    def get_related_forced_due_hours(self):
        self.ensure_one()
        return self.env['hr.forced.due.hours'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '=', self.date)])

    @api.multi
    @api.depends('due_hours')
    def _compute_has_change_day_request(self):
        for att_day in self:
            res = att_day.get_related_forced_due_hours()
            att_day.has_change_day_request = len(res) == 1

    @api.multi
    @api.depends('date')
    def _compute_working_day(self):
        for att_day in self:
            att_day.working_day = fields.Date.from_string(
                att_day.date).strftime('%A').title()

    @api.multi
    @api.depends('working_day')
    def _compute_name(self):
        for rd in self:
            rd.name = rd.working_day + ' ' + rd.date

    @api.multi
    @api.depends('leave_ids', 'public_holiday_id')
    def _compute_in_leave(self):
        for att_day in self:
            att_day.in_leave = att_day.leave_ids or att_day.public_holiday_id

    @api.multi
    @api.depends('working_schedule_id', 'leave_ids', 'public_holiday_id',
                 'cal_att_ids.due_hours')
    def _compute_due_hours(self):
        """First search the due hours based on the contract and after remove
        some hours if they are public holiday or vacation"""
        for att_day in self:

            # Forced due hours (when an user changes work days)
            forced_hours = att_day.get_related_forced_due_hours()
            if forced_hours:
                due_hours = forced_hours.forced_due_hours
            else:
                due_hours = sum(att_day.cal_att_ids.mapped('due_hours'))

            # Public holidays
            if att_day.public_holiday_id:
                att_day.due_hours = 0
                continue

            # Leaves
            due_hours -= att_day.get_leave_time(due_hours)

            if due_hours < 0:
                due_hours = 0
            att_day.due_hours = due_hours

    @api.multi
    @api.depends('attendance_ids.worked_hours')
    def _compute_total_attendance(self):
        for att_day in self.filtered('attendance_ids'):
            att_day.total_attendance = sum(
                att_day.attendance_ids.mapped(
                    'worked_hours') or [0])

    @api.multi
    @api.depends('total_attendance', 'coefficient')
    def _compute_paid_hours(self):
        """
        Paid hours are the sum of the attendances minus the break time
        added by the system and multiply by the coefficient.
        """
        for att_day in self.filtered('attendance_ids'):
            paid_hours = att_day.total_attendance

            # Take only the breaks edited by the system
            breaks = att_day.break_ids.filtered(
                lambda r: r.system_modified and not r.is_offered)

            paid_hours -= sum(breaks.mapped('additional_duration'))
            att_day.paid_hours = paid_hours * att_day.coefficient

    @api.multi
    def _compute_free_break_hours(self):
        for att_day in self:
            att_day.free_breaks_hours = sum(att_day.break_ids.filtered(
                'is_offered').mapped('total_duration') or [0])

    @api.multi
    @api.depends('attendance_ids')
    def _compute_rule_id(self):
        """
        To know which working rule is applied on the day, we deduce the
        free break time offered from the paid hours.
        """
        for att_day in self:
            if att_day.paid_hours:
                hours = att_day.paid_hours - att_day.free_breaks_hours
            else:
                hours = att_day.due_hours - att_day.free_breaks_hours
            if hours < 0:
                hours = 0
            att_day.rule_id = self.env['hr.attendance.rules'].search([
                ('time_from', '<=', hours),
                ('time_to', '>', hours),
            ])

    @api.multi
    def _compute_due_break(self):
        """Calculation of the break duration due depending of
        hr.attendance.rules (only for displaying it in the view)"""
        for att_day in self:
            if att_day.rule_id:
                att_day.due_break_min = att_day.rule_id.due_break
                att_day.due_break_total = att_day.rule_id.due_break_total
            else:
                att_day.due_break_min = 0
                att_day.due_break_total = 0

    @api.multi
    @api.depends('break_ids', 'break_ids.total_duration')
    def _compute_break_total(self):
        for att_day in self:
            att_day.break_total = sum(
                att_day.break_ids.mapped('total_duration') or [0])

    @api.multi
    @api.depends('paid_hours', 'due_hours', 'extra_hours_lost')
    def _compute_extra_hours(self):
        sick_leave = self.env.ref('hr_holidays.holiday_status_sl')
        for att_day in self:
            if sick_leave in att_day.leave_ids. \
                    filtered(lambda r: r.state == 'validate'). \
                    mapped('holiday_status_id'):
                att_day.extra_hours = 0
            else:
                extra_hours = att_day.paid_hours - att_day.due_hours
                att_day.extra_hours = extra_hours - att_day.extra_hours_lost

    @api.multi
    def update_extra_hours_lost(self):
        """
        This will set the extra hours lost based on the balance evolution
        of the employee, which is a SQL view.
        """
        max_extra_hours = float(self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.max_extra_hours', 0.0))
        # First reset the extra hours lost
        self.write({'extra_hours_lost': 0})

        for att_day in self:
            # For whatever reason, the search method is unable to search
            # on employee field (gives wrong search results)! Therefore
            # we use a direct SQL query.
            self.env.cr.execute("""
                SELECT balance FROM extra_hours_evolution_day_report
                WHERE employee_id = %s AND hr_date = %s
            """, [att_day.employee_id.id, att_day.date])
            balance = self.env.cr.fetchone()
            balance = balance[0] if balance else 0

            if balance > max_extra_hours:
                overhead = balance - max_extra_hours
                att_day.extra_hours_lost = min(overhead, att_day.extra_hours)
            else:
                att_day.extra_hours_lost = 0

    @api.multi
    def validate_extend_breaks(self):
        """
        This will extend the break time based on the break attendance rules
        of the day. The paid hours will be recomputed after that.
        """

        def extend_longest_break(extension_duration):
            # Extend the break duration
            att_breaks = att_day.break_ids.filtered(
                lambda r: not r.is_offered)

            if att_breaks:
                att_break = att_breaks.sorted('total_duration')[-1]
            # if not exist create a new one
            else:
                att_break = self.env['hr.attendance.break'].create({
                    'employee_id': att_day.employee_id.id,
                    'attendance_day_id': att_day.id
                })

            att_break.write({
                'additional_duration': extension_duration
            })

        def compute_break_time_to_add(rule):
            breaks_total = sum(
                att_day.break_ids.mapped('total_duration') or [0])
            due_break_total = rule["due_break_total"]
            due_break_min_length = rule["due_break"]

            time_to_add = 0
            break_max = max(
                att_day.break_ids.mapped('total_duration') or [0])
            if break_max < due_break_min_length:
                # We want to extend an non-offered break to at least the
                # minimum value.
                break_max_non_offered = max(att_day.break_ids.filtered(
                    lambda b: not b.is_offered).mapped(
                    'total_duration') or [0])
                time_to_add += due_break_min_length - break_max_non_offered
                breaks_total += time_to_add

            if breaks_total < due_break_total:
                time_to_add += due_break_total - breaks_total

            return time_to_add

        for att_day in self:
            logged_hours = att_day.total_attendance - att_day.free_breaks_hours
            rule = self.env['hr.attendance.rules'].search([
                ('time_to', '>', logged_hours),
                '|', ('time_from', '<=', logged_hours),
                ('time_from', '=', False),
            ])
            time_to_add = compute_break_time_to_add(rule)
            if time_to_add != 0:
                # Ensure we don't fall under another working rule when removing
                # hours from that day
                new_logged_hours = logged_hours - time_to_add
                new_rule = self.env['hr.attendance.rules'].search([
                    ('time_to', '>', new_logged_hours),
                    '|', ('time_from', '<=', new_logged_hours),
                    ('time_from', '=', False),
                ])
                if new_rule != rule:
                    time_to_add = compute_break_time_to_add(new_rule)
                    time_to_add = max(time_to_add, logged_hours -
                                      new_rule.time_to)
                if time_to_add != 0:
                    extend_longest_break(time_to_add)

    ##########################################################################
    #                               ORM METHODS                              #
    ##########################################################################
    @api.model
    def create(self, vals):
        rd = super(HrAttendanceDay, self).create(vals)

        att_date = fields.Date.from_string(rd.date)

        # link to leaves (hr.holidays )
        date_str = fields.Date.to_string(att_date)
        rd.leave_ids = self.env['hr.holidays'].search([
            ('employee_id', '=', rd.employee_id.id),
            ('type', '=', 'remove'),
            ('date_from', '<=', date_str),
            ('date_to', '>=', date_str)])

        # find coefficient
        week_day = att_date.weekday()
        co_ids = self.env['hr.weekday.coefficient'].search([
            ('day_of_week', '=', week_day)]).filtered(
            lambda r: r.category_ids & rd.employee_id.category_ids)
        rd.coefficient = co_ids[0].coefficient if co_ids else 1

        # check public holiday
        if self.env['hr.holidays.public'].is_public_holiday(
                rd.date, rd.employee_id.id):
            holidays_lines = self.env['hr.holidays.public'].get_holidays_list(
                att_date.year, rd.employee_id.id)
            rd.public_holiday_id = holidays_lines.filtered(
                lambda r: r.date == rd.date)

        # find related attendance
        rd.attendance_ids = self.env['hr.attendance'].search([
            ('employee_id', '=', rd.employee_id.id),
            ('date', '=', rd.date),
        ])

        for leave in rd.leave_ids:
            leave._compute_att_day()

        # compute breaks
        rd.compute_breaks()

        return rd

    @api.multi
    def write(self, vals):
        res = super(HrAttendanceDay, self).write(vals)
        if 'paid_hours' in vals or 'coefficient' in vals:
            for att_day in self:
                att_days_future = self.search([
                    ('date', '>=', att_day.date),
                    ('employee_id', '=', att_day.employee_id.id)
                ], order='date')
                att_days_future.update_extra_hours_lost()
        return res

    ##########################################################################
    #                             PUBLIC METHODS                             #
    ##########################################################################
    @api.multi
    def open_attendance_day(self):
        """ Used to bypass opening a attendance in popup mode"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance day',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'current',
        }

    def get_leave_time(self, due_hours):
        """
        Compute leave duration for the day.
        :return: deduction to due hours (in hours)
        :rtype: float [0:24]
        """
        deduction = 0
        for leave in self.leave_ids:
            if leave.state != 'validate' or \
                    leave.holiday_status_id.keep_due_hours:
                continue
            else:
                utc_start = fields.Datetime.from_string(leave.date_from)
                utc_end = fields.Datetime.from_string(leave.date_to)

                # Convert UTC in local timezone
                user_tz = self.employee_id.user_id.tz
                if not user_tz:
                    user_tz = u'UTC'
                local = pytz.timezone(user_tz)
                utc = pytz.timezone('UTC')

                local_start = utc.localize(utc_start).astimezone(local)
                local_end = utc.localize(utc_end).astimezone(local)

                leave_start_date = local_start.date()
                leave_end_date = local_end.date()

                date = fields.Date.from_string(self.date)

                full_day = due_hours

                if leave_start_date < date < leave_end_date:
                    deduction += full_day

                elif date == leave_start_date:
                    # convert time in float
                    start = local_start.hour + local_start.minute / 60.
                    for att in self.cal_att_ids:
                        if att.hour_from <= start < att.hour_to:
                            deduction += att.hour_to - start
                        elif start < att.hour_from:
                            deduction += att.due_hours

                elif date == leave_end_date:
                    # convert time in float
                    end = local_end.hour + local_end.minute / 60.
                    for att in self.cal_att_ids:
                        if att.hour_from < end <= att.hour_to:
                            deduction += end - att.hour_from
                        elif end > att.hour_to:
                            deduction += att.due_hours

                else:
                    _logger.error(
                        "This day doesn't correspond to this leave"
                    )
        return deduction

    @api.multi
    def compute_breaks(self):
        """
        Given the attendance of the employee, check the break time rules
        and compute the break time of the day. This will then trigger the
        computation of the paid hours for the day
        (total attendance - additional break time added)
        :return: None
        """
        att_day_ids = self.filtered('attendance_ids')
        att_day_ids.mapped('break_ids').unlink()
        for att_day in att_day_ids:

            # add the offered break
            free_break = self.env['base.config.settings'].get_free_break()
            if free_break > 0:
                self.env['hr.attendance.break'].create({
                    'employee_id': att_day.employee_id.id,
                    'attendance_day_id': att_day.id,
                    'is_offered': True,
                    'additional_duration': free_break
                })

            att_ids = att_day.attendance_ids
            iter_att = iter(att_ids.sorted(key=lambda r: r.check_in))
            previous_att = iter_att.next()
            while True:
                try:
                    attendance = iter_att.next()
                    self.env['hr.attendance.break'].create(
                        {
                            'employee_id': att_day.employee_id.id,
                            'attendance_day_id': att_day.id,
                            'previous_attendance': previous_att.id,
                            'next_attendance': attendance.id,
                        })
                    previous_att = attendance
                except StopIteration:
                    break

            # Extend the break time if needed
            att_day.validate_extend_breaks()
        self._compute_paid_hours()

    @api.multi
    def recompute_due_hours(self):
        self._compute_total_attendance()
        self._compute_due_hours()
        self._compute_paid_hours()
