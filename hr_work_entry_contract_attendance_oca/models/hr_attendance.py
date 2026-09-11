# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    work_entry_ids = fields.One2many("hr.work.entry", "attendance_id", "Work Entries")
