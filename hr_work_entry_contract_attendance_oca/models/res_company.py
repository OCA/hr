# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_default_attendance_hr_work_entry_type(self):
        return self.env.ref("hr_work_entry.work_entry_type_attendance")

    attendance_hr_work_entry_type_id = fields.Many2one(
        "hr.work.entry.type",
        "Attendance Work Entry Type",
        default=_get_default_attendance_hr_work_entry_type,
    )
