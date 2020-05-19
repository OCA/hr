# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.odoo import api


class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread']

    employee_id = fields.Many2one(
        track_visibility='onchange'
    )
    check_in = fields.Datetime(
        track_visibility='onchange'
    )
    check_out = fields.Datetime(
        track_visibility='onchange'
    )
    time_changed_manually = fields.Boolean(
        string="Time changed",
        required=False,
        compute="_compute_time_changed_manually",
        default=False,
        store=True
    )

    @api.one
    @api.depends('check_in','check_out')
    def _compute_time_changed_manually(self):
        if len(self.message_ids) > 3 and not self.time_changed_manually:
            for message_attendance in self.message_ids:
                if len(message_attendance.tracking_value_ids) > 0:
                    tracking_filtered = message_attendance.tracking_value_ids.filtered(lambda t: t.old_value_datetime and (t.field =='check_in' or t.field =='check_out'))
                    if tracking_filtered:
                        self.time_changed_manually = True

    def write(self,values):
        result = super(HrAttendance, self).write(values)
        if len(self.message_ids) > 3 and not self.time_changed_manually:
            self._compute_time_changed_manually()
            self.write(values)
        return result


