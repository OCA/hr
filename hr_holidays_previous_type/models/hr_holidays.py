# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, exceptions, _


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
