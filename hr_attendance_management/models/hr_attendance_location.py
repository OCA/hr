# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class HrAttendanceLocation(models.Model):
    _name = "hr.attendance.location"
    _description = "Attendance Location"

    ##########################################################################
    #                                 FIELDS                                 #
    ##########################################################################

    name = fields.Char()
