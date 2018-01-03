# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    theoretical_hours = fields.Float(
        compute="_compute_theoretical_hours",
        store=True,
        compute_sudo=True,
    )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """Don't show anything for this measure in the attendances report."""
        res = super(HrAttendance, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy,
        )
        if 'theoretical_hours' not in fields:
            return res
        for line in res:
            del line['theoretical_hours']
        return res

    @api.depends('check_in', 'employee_id')
    def _compute_theoretical_hours(self):
        obj = self.env['hr.attendance.theoretical.time.report']
        for record in self:
            record.theoretical_hours = obj._theoretical_hours(
                record.employee_id, record.check_in,
            )
