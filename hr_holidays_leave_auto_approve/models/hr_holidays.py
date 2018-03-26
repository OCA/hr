# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def _check_state_access_right(self, vals):
        if self.env['res.users'].browse(self.env.uid)._is_admin():
            return True
        return super(HrHolidays, self)._check_state_access_right(vals)

    @api.model
    def create(self, values):
        auto_approve = self._get_auto_approve_on_creation(values)
        res = super(
            HrHolidays, self.with_context(
                tracking_disable=auto_approve)
            ).create(values)
        if self.sudo().env.user.has_group(
                'hr_holidays.group_hr_holidays_user'):
            if res.holiday_status_id and res.holiday_status_id.auto_approve:
                res.sudo().action_approve()
        return res

    @api.model
    def _get_auto_approve_on_creation(self, values):
        auto_approve = False
        if values.get('holiday_status_id'):
            auto_approve = self.env['hr.holidays.status'].browse(
                values.get('holiday_status_id')
            ).auto_approve
        return auto_approve
