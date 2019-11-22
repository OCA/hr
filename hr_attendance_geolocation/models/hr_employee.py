# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def attendance_manual(self, next_action, entered_pin=False,
                          location=False):
        res = super(HrEmployee, self.with_context(
            attendance_location=location)).attendance_manual(
            next_action, entered_pin)
        return res

    @api.multi
    def attendance_action_change(self):
        res = super().attendance_action_change()
        location = self.env.context.get('attendance_location', False)
        if location:
            if self.attendance_state == 'checked_in':
                res.write({
                    'check_in_latitude': location[0],
                    'check_in_longitude': location[1],
                })
            else:
                res.write({
                    'check_out_latitude': location[0],
                    'check_out_longitude': location[1],
                })
        return res
