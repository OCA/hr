# Copyright 2019 Creu Blanca
# Copyright 2020 Landoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import timedelta


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
    @api.depends('message_ids.tracking_value_ids')
    def _compute_time_changed_manually(self):
        if not self.time_changed_manually:
            # For manual attendance, tolerance to consider it acceptable
            tolerance = timedelta(seconds=60)
            for tracking in self.message_ids.mapped('tracking_value_ids'):
                if (tracking.field in ['check_in', 'check_out']):
                    # Attendance created from kiosk or check-in/check-out screen
                    if tracking.old_value_datetime:
                        self.time_changed_manually = True
                    # Attendance created in form view, if check-in and check-out are in admitted tolerance,
                    # they will not be considered "manually changed"
                    else:
                        diff = abs(tracking.new_value_datetime - tracking.mail_message_id.date)
                        if diff > tolerance:
                            self.time_changed_manually = True
