# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    theoretical_hours = fields.Float(
        compute="_compute_theoretical_hours", store=True, compute_sudo=True
    )

    @api.depends("check_in", "employee_id")
    def _compute_theoretical_hours(self):
        obj = self.env["hr.attendance.theoretical.time.report"]
        for record in self:
            record.theoretical_hours = obj._theoretical_hours(
                record.employee_id, record.check_in
            )
