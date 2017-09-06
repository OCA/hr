# -*- coding: utf-8 -*-
from odoo import fields, models


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    real_check_in = fields.Datetime(required=True)
    real_check_out = fields.Datetime()
    needs_approval = fields.Boolean()
