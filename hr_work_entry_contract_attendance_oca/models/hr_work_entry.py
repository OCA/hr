# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    attendance_id = fields.Many2one("hr.attendance", "Attendance")
