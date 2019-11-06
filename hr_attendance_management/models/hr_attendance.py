# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    attendance_day_id = fields.Many2one(comodel_name='hr.attendance.day',
                                        string='Attendance day',
                                        readonly=True)

    date = fields.Date('Date', compute='_compute_date', store=True)
    due_hours = fields.Float(related='attendance_day_id.due_hours',
                             readonly=True)
    total_attendance = fields.Float(
        related='attendance_day_id.total_attendance', readonly=True)
    has_change_day_request = fields.Boolean(
        related='attendance_day_id.has_change_day_request', readonly=True)
    location_id = fields.Many2one('hr.attendance.location', 'Location')

    # Link the resource.calendar to the attendance thus we keep a trace of
    # due_hours
    working_schedule_id = fields.Many2one('resource.calendar',
                                          string='Working schedule')

    ##########################################################################
    #                             VIEW CALLBACKS                             #
    ##########################################################################
    @api.multi
    def open_attendance(self):
        """ Used to bypass opening a attendance in popup mode from
        hr_attendance_day view. """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'current',
        }

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    @api.multi
    @api.depends('check_in')
    def _compute_date(self):
        for attendance in self.filtered('check_in'):
            date = fields.Date.from_string(attendance.check_in)
            attendance.date = fields.Date.to_string(date)

    ##########################################################################
    #                               ORM METHODS                              #
    ##########################################################################
    @api.model
    def create(self, vals):
        """ If the corresponding attendance day doesn't exist a new one is
        created"""
        new_record = super(HrAttendance, self).create(vals)
        att_day = new_record._find_related_day()
        new_record.attendance_day_id = att_day
        new_record.working_schedule_id = att_day.working_schedule_id
        att_day.compute_breaks()
        return new_record

    @api.multi
    def write(self, vals):
        att_day_updated = self.env['hr.attendance']
        if 'check_in' in vals:
            # Check if the date of check_in has changed and change the
            # attendance_day
            for att in self:
                old_check_in = fields.Date.from_string(att.check_in)
                check_in = fields.Date.from_string(vals['check_in'])
                if old_check_in != check_in:
                    # Update break time of old attendance day
                    att._find_related_day()
                    # Save attendance to update attendance days after writing
                    # the change.
                    att_day_updated += att
        if 'check_out' in vals:
            # Update breaks
            att_day_updated = self

        res = super(HrAttendance, self).write(vals)
        att_day_updated._find_related_day()
        return res

    def _find_related_day(self):
        """
        Finds the existing attendance day or create one if it doesn't exist
        Called when an attendance is mapped to an attendance day
        :return: hr.attendance.day record
        """
        attendance_days = self.env['hr.attendance.day']
        for attendance in self:
            date = fields.Date.from_string(attendance.check_in)
            employee_id = attendance.employee_id.id
            attendance_day = self.env['hr.attendance.day'].search([
                ('employee_id', '=', employee_id),
                ('date', '=', date)
            ])
            if not attendance_day:
                attendance_day = self.env['hr.attendance.day'].create({
                    'employee_id': employee_id,
                    'date': fields.Date.to_string(date)
                })
            else:
                # A modified attendance should update related breaks
                attendance_day.compute_breaks()
            attendance_days |= attendance_day
        return attendance_days
