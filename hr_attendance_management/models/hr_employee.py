# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    extra_hours_continuous_cap = fields.Boolean(
        help="Set this field to true if you want to have the employee "
             "extra hours to be continuously capped to max_extra_hours and not"
             " only at the cron execution time.")
    current_period_start_date = fields.Date(  # TODO: check to remove!
        compute="_compute_current_period_start_date", store=False)

    attendance_days_ids = fields.One2many('hr.attendance.day', 'employee_id',
                                          "Attendance days")
    balance = fields.Float('Balance', compute='compute_balance', store=True)
    initial_balance = fields.Float('Initial Balance')

    extra_hours_lost = fields.Float()

    balance_formatted = fields.Char(string="Balance",
                                    compute='_compute_formatted_hours')

    time_warning_balance = fields.Char(compute='_compute_time_warning_balance')

    time_warning_today = fields.Char(compute='_compute_time_warning_today')

    extra_hours_today = fields.Char(compute='_compute_extra_hours_today')

    today_hour = fields.Char(compute='_compute_today_hour')

    today_hour_formatted = fields.Char(compute='_compute_today_hour_formatted')

    work_location_id = fields.Many2one('hr.attendance.location',
                                       string='Work Location')

    work_location = fields.Char(compute='_compute_work_location')

    period_ids = fields.One2many('hr.employee.period', 'employee_id',
                                 string='History Periods', readonly=True,
                                 compute="_compute_periods")

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################

    @api.multi
    def _compute_current_period_start_date(self):
        for employee in self:
            previous_periods = \
                employee.period_ids.filtered(
                    lambda e: e.end_date <= fields.Date.today())
            if previous_periods:
                previous_period = previous_periods.sorted(key=lambda e: e.end_date)[-1]
                employee.current_period_start_date = \
                    fields.Date.from_string(previous_period.end_date)
            else:
                config = self.env['base.config.settings'].create({})
                employee.current_period_start_date = \
                    config.get_beginning_date_for_balance_computation()

    @api.multi
    def _compute_work_location(self):
        for employee in self:
            actual_location = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)], limit=1)
            employee.work_location = actual_location.location_id.name

    @api.multi
    @api.depends('initial_balance', 'attendance_days_ids.paid_hours')
    def _compute_periods(self):
        for employee in self:
            employee.period_ids = self.env['hr.employee.period'].search([
                ('employee_id', '=', employee.id)
            ], order="start_date asc")
            if len(employee.period_ids) != 0:
                employee.period_ids[0].update_period()

    @api.multi
    @api.depends('initial_balance', 'attendance_days_ids.paid_hours')
    def compute_balance(self, store=False):
        """
        Method used to compute balance we needed. It uses the history of the employee to avoid
        recalculating the whole balance each time.
        This is also the method used to add a new history entry (by the CRON e.g.)
        :param store: create a new period from the last one to current day and store it if True
        """
        for employee in self:
            config = self.env['base.config.settings'].create({})
            config.set_beginning_date()
            # Compute from 01.01.2018 as default
            balance = employee.initial_balance
            start_date = config.get_beginning_date_for_balance_computation()
            end_date = fields.Date.today()
            final_balance = None

            if employee.period_ids:
                employee_history_sorted = \
                    employee.period_ids.sorted(key=lambda r: r.end_date)
                start_date = \
                    fields.Date.from_string(employee_history_sorted[-1].end_date)
                # If there is an history for this employee, take values of last period
                if start_date < fields.Date.from_string(end_date):
                    balance = employee_history_sorted[-1].final_balance
                # If last period goes to today.
                elif start_date == fields.Date.from_string(end_date):
                    final_balance = employee_history_sorted[-1].final_balance
                # If the period goes to today, recompute from 01.01.2018
                else:
                    start_date = config.get_beginning_date_for_balance_computation()

            extra = None
            lost = None
            if final_balance and not employee.extra_hours_continuous_cap:
                employee.balance = final_balance
                employee.extra_hours_lost = 0
            # If final_balance is not None,
            # it means there is a period with end_date == today
            # so we just assign the value. The cap is taken in consideration here.
            elif final_balance:
                max_extra_hours = self.env['base.config.settings'].create({}) \
                    .get_max_extra_hours()
                bal = min(max_extra_hours, final_balance)
                employee.balance = bal
                # if we capped the hours
                if bal == max_extra_hours:
                    employee.extra_hours_lost = final_balance - max_extra_hours
            else:
                extra, lost = employee.past_balance_computation(
                    start_date=start_date,
                    end_date=end_date,
                    existing_balance=balance)

                employee.balance = extra
                employee.extra_hours_lost = lost

            if store:
                previous_period_id = None
                if employee.period_ids:
                    previous_period = \
                        employee.period_ids.sorted(key=lambda r: r.end_date)[-1]
                    previous_period_id = previous_period.id

                self.create_period(employee.id,
                                   start_date,
                                   end_date,
                                   extra,
                                   previous_period_id,
                                   lost,
                                   employee.extra_hours_continuous_cap)

    def create_period(self, employee_id, start_date, end_date, balance,
                      previous_period, lost_hours, continuous_cap):
        return self.env['hr.employee.period'].create({
            'employee_id': employee_id,
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_period': previous_period,
            'lost': lost_hours,
            'continuous_cap': continuous_cap
        })

    @api.multi
    def is_continuous_cap_at_date(self, date):
        """
        This method return the status of the employee at the specified date.
        A True value means that the employee was capped to max_extra_hours at
        the specified date.
        Can Raise a ValueError if we don't have information about the period in
        which date is.
        :param date: The date of the desired status
        :return: Boolean whether it was a continuous or annual capping.
        """

        for employee in self:
            period = self.env['hr.employee.period'].search([
                ('employee_id', '=', employee.id),
                ('start_date', '<=', date),
                ('end_date', '>', date)
            ], order='start_date asc', limit=1)
            if period:
                return period.continuous_cap
            else:
                return employee.extra_hours_continuous_cap

    @api.multi
    def complete_balance_computation(self, start_date=None, end_date=None,
                                     existing_balance=0):
        """
        Compute the running balances extra and lost hours of the employee
        between start and end date. We go through the days and add the paid
        hours, keeping an array of the value at each day.
        :param start_date: Start date of the period of interest
        :param end_date: End date of the period of interest
        :param existing_balance: The extra hours balance of the employee at
                                 start_date
        :return: 3 lists:
                 (a) list of each date for which we have data, sorted
                 (b) the corresponding cumulative sum of extra hours for each
                     day present in (a)
                 (c) the cumulative sum of lost hours for each day in (a).
                     (increasing values as no lost hours can be deduced).
        """
        self.ensure_one()
        max_extra_hours = self.env['base.config.settings'].create({})\
            .get_max_extra_hours()
        if not start_date:
            start_date = fields.Date.to_string(
                fields.Date.today().replace(month=1, day=1))
        if not end_date:
            end_date = \
                fields.Date.to_string(fields.Date.today() + datetime.timedelta(days=1))

        if not isinstance(start_date, basestring):
            start_date = fields.Date.to_string(start_date)
        if not isinstance(end_date, basestring):
            end_date = fields.Date.to_string(end_date)

        if start_date > end_date:
            raise ValidationError("Start date must be earlier than end date.")

        attendance_day_ids = self.attendance_days_ids.filtered(
            lambda r: start_date <= r.date < end_date)

        days = [start_date]
        extra_hours_sum = [existing_balance]
        lost_hours = [0]
        attendance_days_sorted = sorted(attendance_day_ids,
                                        key=lambda r: r.date)
        for day in attendance_days_sorted:
            days.append(day.date)
            extra_hours_sum.append(extra_hours_sum[-1] + day.day_balance)
            lost_hours.append(lost_hours[-1])
            if extra_hours_sum[-1] > max_extra_hours and \
                    self.is_continuous_cap_at_date(day.date):
                lost_hours[-1] += extra_hours_sum[-1] - max_extra_hours
                extra_hours_sum[-1] = max_extra_hours

        return days, extra_hours_sum, lost_hours

    @api.multi
    def past_balance_computation(self, start_date=None, end_date=None,
                                 existing_balance=0):
        """
        Compute the balance of extra and lost horus at end_date.
        :param start_date: Start date of the computation
        :param end_date: Date of desired data
        :param existing_balance: Existing extra hours balance at start_date
        :return: Tuple of integers (extra_hours, lost_hours)
        """
        _, extra_hours_sum, lost_hours = self.complete_balance_computation(
            start_date=start_date,
            end_date=end_date,
            existing_balance=existing_balance)
        if len(extra_hours_sum) < 1:
            _logger.warning("Balance computation on period without data")
            return 0, 0
        return extra_hours_sum[-1], lost_hours[-1]

    @api.model
    def _cron_create_attendance(self, domain=None, day=None):
        att_day = self.env['hr.attendance.day']
        employees = self.search(domain or [])
        if day is None:
            day = fields.Date.today()
        for employee in employees:
            # check if an entry already exists. If yes, it will not be
            # recreated
            att_days = att_day.search(
                [('date', '=', day), ('employee_id', '=', employee.id)])
            if att_days:
                continue

            # check that the employee is currently employed.
            contracts_valid_today = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('date_start', '<=', day),
                '|', ('date_end', '=', False), ('date_end', '>=', day)
            ])

            if not att_days and contracts_valid_today:
                att_day.create({
                    'date': day,
                    'employee_id': employee.id
                })

    @api.model
    def _cron_compute_annual_balance(self):
        """
        Roll over the balance of extra hours for the period ranging from the
        last call to this cron to today. The balance of the previous period
        will be stored for recomputation in case of change.
        :return: Nothing
        """
        employees = self.search([])
        for employee in employees:
            employee.compute_balance(store=True)

    @api.multi
    @api.depends('today_hour')
    def _compute_extra_hours_today(self):
        for employee in self:
            employee.extra_hours_today = \
                employee.convert_hour_to_time(employee.today_hour)

    @api.multi
    def _compute_time_warning_balance(self):
        max_extra_hours = self.env['base.config.settings'].create({}) \
            .get_max_extra_hours()
        for employee in self:
            if employee.balance < 0:
                employee.time_warning_balance = 'red'
            elif max_extra_hours and \
                    employee.balance >= max_extra_hours * 2 / 3:
                employee.time_warning_balance = 'orange'
            else:
                employee.time_warning_balance = 'green'

    @api.multi
    @api.depends('today_hour')
    def _compute_time_warning_today(self):
        for employee in self:
            employee.time_warning_today = \
                'red' if float(employee.today_hour) < 0 else 'green'

    @api.multi
    def _compute_today_hour(self):
        for employee in self:
            current_att_day = self.env['hr.attendance.day'].search([
                ('employee_id', '=', employee.id),
                ('date', '=', fields.Date.today())])
            employee.today_hour = \
                employee.calc_today_hour() - current_att_day.due_hours

    @api.multi
    def _compute_formatted_hours(self):
        for employee in self:
            employee.balance_formatted = \
                employee.convert_hour_to_time(employee.balance)

    @api.multi
    @api.depends('today_hour')
    def _compute_today_hour_formatted(self):
        for employee in self:
            today_hour = employee.calc_today_hour()
            employee.today_hour_formatted = \
                employee.convert_hour_to_time(today_hour)

    @api.model
    def convert_hour_to_time(self, hour):
        formatted = '{:02d}:{:02d}'.format(*divmod(int(abs(
            float(hour) * 60)), 60))
        return '-' + formatted if hour < 0 else formatted

    # TODO base it on att_day.total_attendance
    @api.multi
    def calc_today_hour(self):
        self.ensure_one()

        today = fields.Date.today()
        attendances_today = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_in', '>=', today)
        ])
        worked_hours = 0

        for attendance in attendances_today:
            if attendance.check_out:
                worked_hours += attendance.worked_hours
            else:
                delta = datetime.datetime.now() - \
                        fields.Datetime.from_string(attendance.check_in)
                worked_hours += delta.total_seconds() / 3600.0
        return worked_hours

    def open_balance_graph(self):
        """
        Populates data for history graph and open the view
        :return: action opening the view
        """
        self.ensure_one()
        self.env['balance.evolution.graph'].populate_graph(self.id)
        return {
            'name': 'Extra hours evolution',
            'type': 'ir.actions.act_window',
            'res_model': 'balance.evolution.graph',
            'context': {"graph_mode": "bar"},
            'view_type': 'form',
            'view_mode': 'graph',
            'domain': [('employee_id', '=', self.id)],
            'target': 'current',
        }
