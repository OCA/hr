# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta, date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrAttendanceSettings(models.TransientModel):
    """ Settings configuration for hr.attendance."""
    _inherit = 'base.config.settings'

    free_break = fields.Float('Free break (hour)')
    max_extra_hours = fields.Float('Max extra hours')

    last_balance_cron_execution = fields.Date(
        'Date of last yearly balance computation', readonly=True)
    next_balance_cron_execution = fields.Date(
        'Next date for computation of annual extra hours. It will be executed'
        ' yearly from then on')

    ##########################################################################
    #                             PUBLIC METHODS                             #
    ##########################################################################
    @api.multi
    def set_free_break(self):
        self.ensure_one()
        if self.free_break < 0:
            raise ValidationError("Free break should be positive")
        if self.free_break != self.get_free_break():
            self.env['ir.config_parameter'].set_param(
                'hr_attendance_management.free_break', str(self.free_break))

    @api.multi
    def set_max_extra_hours(self):
        if self.max_extra_hours < 0:
            raise ValidationError("Max extra hours should be positive")
        # rounding is needed as postgres use less decimal place than python
        if round(self.max_extra_hours, 10) != self.get_max_extra_hours():
            self.env['ir.config_parameter'].set_param(
                'hr_attendance_management.max_extra_hours',
                str(self.max_extra_hours))

    @api.model
    def update_balance_cron_date(self):
        self.env['ir.config_parameter'].set_param(
            'hr_attendance_management.penultimate_balance_cron_execution',
            self.get_last_balance_cron_execution())
        self.env['ir.config_parameter'].set_param(
            'hr_attendance_management.last_balance_cron_execution',
            date.today())
        # self.env['hr.employee'].search([]).past_extra_hours_computation(
        #     start_date=fields.Date.from_string(
        #         self.get_penultimate_extra_hours_cron_execution()),
        #     end_date=fields.Date.from_string(
        #         self.get_last_extra_hours_cron_execution()))

    @api.multi
    def set_next_balance_cron_execution(self):
        self.ensure_one()
        last = fields.Date.from_string(
            self.get_last_balance_cron_execution())
        current = fields.Date.from_string(
            self.get_next_balance_cron_execution())
        proposed = fields.Date.from_string(self.next_balance_cron_execution)
        if current > proposed and last.replace(year=last.year + 1) > proposed:
            # would error if last is 29th February
            raise ValidationError("The chosen date should be further in the "
                                  "future than the current one or at least one"
                                  " year away.")
        self.env.ref(
            'hr_attendance_management.'
            'ir_cron_compute_annual_balance') \
            .nextcall = self.next_balance_cron_execution

    @api.model
    def get_default_values(self, _fields):
        return {
            'free_break': self.get_free_break(),
            'max_extra_hours': self.get_max_extra_hours(),
            'last_balance_cron_execution':
                self.get_last_balance_cron_execution(),
            'next_balance_cron_execution':
                self.get_next_balance_cron_execution()
        }

    @api.model
    def get_free_break(self):
        return float(self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.free_break', '0.0'))

    @api.model
    def get_max_extra_hours(self):
        return float(self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.max_extra_hours', '0.0'))

    @api.model
    def get_penultimate_balance_cron_execution(self):
        return self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.penultimate_balance_cron_execution',
            str(date.today().year - 1) + '-01-01')

    @api.model
    def get_last_balance_cron_execution(self):
        # cron write_date is not sufficient as it is also updated on frequency
        # changes
        return self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.last_balance_cron_execution',
            str(date.today().year) + '-01-01')

    @api.model
    def get_next_balance_cron_execution(self):
        try:
            return self.env.ref(
                'hr_attendance_management.'
                'ir_cron_compute_annual_balance') \
                .nextcall
        except Exception:
            # CRON not yet created. We are in module installation
            return None


class CreateHrAttendance(models.TransientModel):
    _name = 'create.hr.attendance.day'

    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    employee_ids = fields.Many2many('hr.employee', string='Employee')

    def create_attendance_day(self):
        date_to = fields.Date.from_string(self.date_to)
        att_day = self.env['hr.attendance.day']

        for employee_id in self.employee_ids:
            current_date = fields.Date.from_string(self.date_from)
            while current_date <= date_to:
                already_exist = att_day.search([
                    ('employee_id', '=', employee_id.id),
                    ('date', '=', current_date)
                ])
                if not already_exist:
                    att_day.create({
                        'employee_id': employee_id.id,
                        'date': current_date,
                    })
                current_date = current_date + timedelta(days=1)
