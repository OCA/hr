# -*- coding: utf-8 -*-
# Copyright 2021 ForgeFlow S.L.

from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    is_check_in_rfid = fields.Boolean()
    is_check_out_rfid = fields.Boolean()
