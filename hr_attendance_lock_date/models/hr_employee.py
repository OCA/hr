# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    attendance_lock_date = fields.Datetime('Attendance lock date')
