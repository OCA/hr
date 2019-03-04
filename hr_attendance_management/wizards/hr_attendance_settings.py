# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta, date

from odoo import models, fields, api


class HrAttendanceSettings(models.TransientModel):
    """ Settings configuration for hr.attendance."""
    _inherit = 'base.config.settings'

    free_break = fields.Float('Free break (hour)')
    max_extra_hours = fields.Float('Max extra hours')

    ##########################################################################
    #                             PUBLIC METHODS                             #
    ##########################################################################
    @api.multi
    def set_free_break(self):
        self.env['ir.config_parameter'].set_param(
            'hr_attendance_management.free_break',
            str(self.free_break))

    @api.multi
    def set_max_extra_hours(self):
        self.env['ir.config_parameter'].set_param(
            'hr_attendance_management.max_extra_hours',
            str(self.max_extra_hours))
        # We should compute again the extra hours lost for the year
        self.env['hr.attendance.day'].search([
            ('date', '>=', date.today().strftime('%Y-01-01'))
        ]).update_extra_hours_lost()

    @api.model
    def get_default_values(self, _fields):
        param_obj = self.env['ir.config_parameter']
        return {
            'free_break': float(param_obj.get_param(
                'hr_attendance_management.free_break', '0.0')),
            'max_extra_hours': float(param_obj.get_param(
                'hr_attendance_management.max_extra_hours', '0.0')),
        }

    @api.model
    def get_free_break(self):
        return float(self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.free_break'))

    @api.model
    def get_max_extra_hours(self):
        return float(self.env['ir.config_parameter'].get_param(
            'hr_attendance_management.max_extra_hours'))


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
