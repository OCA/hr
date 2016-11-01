# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def _check_state_access_right(self, vals):
        if self.env['res.users'].browse(self.env.uid)._is_admin():
            return True
        return super(HrHolidays, self)._check_state_access_right(vals)

    @api.model
    def create(self, values):
        res = super(HrHolidays, self).create(values)
        if self.env.user.sudo().has_group(
                'hr_holidays.group_hr_holidays_user'):
            if res.holiday_status_id and res.holiday_status_id.auto_approve:
                res.sudo().action_approve()
        return res
