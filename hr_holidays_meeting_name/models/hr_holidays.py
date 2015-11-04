# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_meeting_name,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_meeting_name is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_meeting_name is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_meeting_name.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    use_leave_name_for_meeting = fields.Boolean(
        string='Use leave name for meeting description', default=True)
    meeting_description = fields.Char(translate=True)


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def _prepare_holidays_meeting_values(self, leave):
        res = super(HrHolidays, self)._prepare_holidays_meeting_values(leave)
        if not leave.holiday_status_id.use_leave_name_for_meeting and \
                leave.holiday_status_id.meeting_description:
            res['name'] = leave.holiday_status_id.meeting_description
        return res
