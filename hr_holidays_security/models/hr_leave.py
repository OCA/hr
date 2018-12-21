# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    can_view_name = fields.Boolean(
        string='Can View Name',
        compute='_compute_can_view_name',
    )
    report_note = fields.Text(
        groups='hr_holidays.group_hr_holidays_manager',
    )

    @api.multi
    def _compute_can_view_name(self):
        has_group_hr_holidays_user = self.user_has_groups(
            'hr_holidays.group_hr_holidays_user'
        )

        for leave in self:
            leave.can_view_name = has_group_hr_holidays_user \
                or leave.employee_id.user_id.id == self.env.uid
