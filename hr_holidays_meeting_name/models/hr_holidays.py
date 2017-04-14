# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    use_leave_name_for_meeting = fields.Boolean(
        string='Use leave name for meeting description', default=True)
    meeting_description = fields.Char(translate=True)


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def _prepare_holidays_meeting_values(self):
        res = super(HrHolidays, self)._prepare_holidays_meeting_values()
        if not self.holiday_status_id.use_leave_name_for_meeting and \
                self.holiday_status_id.meeting_description:
            res['name'] = self.holiday_status_id.meeting_description
        return res
