# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_previous_type,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_previous_type is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_previous_type is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_previous_type.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    previous_type_id = fields.Many2one(comodel_name='hr.holidays.status',
                                       string='Previous Type')


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.constrains('holiday_status_id', 'date_from', 'date_to', 'employee_id')
    @api.one
    def _check_previous_type_remaining_leaves(self):
        if self.type == 'remove' and \
                self.holiday_status_id.previous_type_id.id:
            check_previous_type_days = False
            previous_type = self.holiday_status_id.previous_type_id
            if previous_type.use_validity_dates:
                if self.date_from <= previous_type.date_end:
                    check_previous_type_days = True
            else:
                check_previous_type_days = True
            if check_previous_type_days:
                leaves = previous_type.get_days(self.employee_id.id)
                if leaves[previous_type.id]['virtual_remaining_leaves'] > 0:
                    name = self.holiday_status_id.name
                    if previous_type.date_end:
                        tz_date_end = self._utc_to_tz(previous_type.date_end)
                        raise exceptions.Warning(
                            _("""You have to take your remaining leave
                            on %s before %s. the remaining leaves in this type
                            are valid until %s""") % (previous_type.name,
                                                      name,
                                                      tz_date_end))
                    else:
                        raise exceptions.Warning(
                            _("""You have to take your remaining leave
                            on %s before %s.""") % (previous_type.name,
                                                    name))
