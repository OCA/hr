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
    def action_validate(self):
        res = super(HrHolidays, self).action_validate()
        for record in self:
            leave_type = record.holiday_status_id
            if record.meeting_id and\
                    not leave_type.use_leave_name_for_meeting and \
                    leave_type.meeting_description:
                record.meeting_id.name =\
                    record.holiday_status_id.meeting_description
        return res
