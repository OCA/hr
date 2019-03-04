# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class HrAttendanceBreak(models.Model):
    _name = "hr.attendance.break"
    _description = "Attendance break"

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################

    name = fields.Char(compute='_compute_name')
    employee_id = fields.Many2one('hr.employee', "Employee", required=True)
    attendance_day_id = fields.Many2one(
        'hr.attendance.day', "Attendance day", required=True,
        ondelete="cascade")

    original_duration = fields.Float(
        compute='_compute_original_duration', store=True)
    additional_duration = fields.Float('Duration added by the rules')
    total_duration = fields.Float(
        'Break duration', readonly=True, compute='_compute_total_duration',
        store=True, oldname='logged_duration')

    is_offered = fields.Boolean()
    system_modified = fields.Boolean(
        'Modified by the system', compute='_compute_system_modified')

    start = fields.Datetime(compute='_compute_start_stop', store=True)
    stop = fields.Datetime(compute='_compute_start_stop', store=True)

    previous_attendance = fields.Many2one('hr.attendance')
    next_attendance = fields.Many2one('hr.attendance')

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    @api.depends('start', 'stop')
    @api.multi
    def _compute_name(self):
        for rd in self:
            if rd.is_offered:
                rd.name = 'Free break'
            elif not rd.start:
                rd.name = 'Created by the system'
            else:
                # Insert the beginning/end time of the break in is name
                start = fields.Datetime.context_timestamp(
                    rd.employee_id, fields.Datetime.from_string(rd.start))
                stop = fields.Datetime.context_timestamp(
                    rd.employee_id, fields.Datetime.from_string(rd.stop))
                rd.name = start.strftime('%H:%M') + ' - ' + stop.strftime(
                    '%H:%M')

    @api.multi
    @api.depends('previous_attendance')
    def _compute_start_stop(self):
        for rd in self:
            rd.start = rd.previous_attendance.check_out
            rd.stop = rd.next_attendance.check_in

    @api.multi
    @api.depends('start', 'stop')
    def _compute_original_duration(self):
        for att_break in self:
            if not att_break.stop:
                att_break.original_duration = 0
            else:
                start = fields.Datetime.from_string(att_break.start)
                stop = fields.Datetime.from_string(att_break.stop)
                delta = stop - start
                att_break.original_duration = delta.total_seconds() / 3600.0

    @api.multi
    @api.depends('original_duration', 'additional_duration')
    def _compute_total_duration(self):
        for rd in self:
            rd.total_duration = rd.original_duration + rd.additional_duration

    @api.multi
    @api.depends('additional_duration')
    def _compute_system_modified(self):
        for rd in self:
            rd.system_modified = bool(rd.additional_duration)
