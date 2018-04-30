# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Stephane Eicher <seicher@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import models, fields, api


class HrAttendanceRules(models.Model):
    _name = 'hr.attendance.rules'
    _description = "HR attendance break time rule"

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################
    name = fields.Char('Name', compute='_compute_name')
    time_from = fields.Float(
        'From', help='Threshold in hours when the duration break change')
    time_to = fields.Float('To', help='In hour')
    due_break = fields.Float('Minimum break', help='In hour')
    due_break_total = fields.Float('Total break', help='In hour')

    ##########################################################################
    #                             FIELDS METHODS                             #
    ##########################################################################
    @api.multi
    @api.depends('time_from', 'time_to')
    def _compute_name(self):
        for this in self:
            this.name = str(int(this.time_from)) + ' - ' + str(int(
                this.time_to))
