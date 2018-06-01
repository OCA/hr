# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Eicher Stephane <seicher@compassion.ch>
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    attendance_day_id = fields.Many2one(comodel_name='hr.attendance.day',
                                        string='Attendance day',
                                        readonly=True)

    due_hours = fields.Float(related='attendance_day_id.due_hours')
    total_attendance = fields.Float(
        related='attendance_day_id.total_attendance')
    has_change_day_request = fields.Boolean(
        related='attendance_day_id.has_change_day_request')

    ##########################################################################
    #                               ORM METHODS                              #
    ##########################################################################
    @api.model
    def create(self, vals):
        """ If the corresponding attendance day doesn't exist a new one is
        created"""
        new_record = super(HrAttendance, self).create(vals)
        new_record.attendance_day_id = new_record._find_related_day()
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

    def _find_related_day(self):
        """
        Finds the existing attendance day or create one if it doesn't exist
        Called when an attendance is mapped to an attendance day
        :return: hr.attendance.day record
        """
        attendance_days = self.env['hr.attendance.day']
        for attendance in self:
            date = attendance.check_in[:10]
            employee_id = attendance.employee_id.id
            attendance_day = self.env['hr.attendance.day'].search([
                ('employee_id', '=', employee_id),
                ('date', '=', date)
            ])
            if not attendance_day:
                attendance_day = self.env['hr.attendance.day'].create({
                    'employee_id': employee_id,
                    'date': date
                })
            else:
                # A modified attendance should update related breaks
                attendance_day.compute_breaks()
            attendance_days |= attendance_day
        return attendance_days
