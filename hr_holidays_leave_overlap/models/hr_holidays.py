# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def create(self, values):
        if values.get('type', False) == 'remove':

            values['employee_id'] = values.get('employee_id', False)
            values['category_id'] = values.get('category_id', False)

            including = self.search([
                ('date_from', '<', values['date_from']),
                ('date_to', '>', values['date_to']),
                ('employee_id', '=', values['employee_id']),
                ('category_id', '=', values['category_id']),
                ('type', '=', values['type']),
                ('state', 'not in', ['cancel', 'refuse']),
            ], limit=1)
            if including:
                raise ValidationError(_(
                    'You are trying to create a leave on a period which is '
                    'already completely covered by a different leave!')
                )

            base_date = [values['date_from'], values['date_to']]
            split_date = []
            stepping_date = []

            left_overlapping = self.search([
                ('date_from', '<', values['date_from']),
                ('date_to', '>', values['date_from']),
                ('date_to', '<=', values['date_to']),
                ('employee_id', '=', values['employee_id']),
                ('category_id', '=', values['category_id']),
                ('type', '=', values['type']),
                ('state', 'not in', ['cancel', 'refuse']),
            ], limit=1)

            for leave in left_overlapping:
                base_date[0] = fields.Datetime.to_string(
                    fields.Datetime.from_string(leave.date_to) +
                    timedelta(seconds=1)
                )

            included = self.search([
                ('date_from', '>=', values['date_from']),
                ('date_to', '<=', values['date_to']),
                ('employee_id', '=', values['employee_id']),
                ('category_id', '=', values['category_id']),
                ('type', '=', values['type']),
                ('state', 'not in', ['cancel', 'refuse']),
            ], order='date_from ASC')

            for leave in included:
                if not stepping_date and base_date[0] == leave.date_from:
                    base_date[0] = fields.Datetime.to_string(
                        fields.Datetime.from_string(leave.date_to) +
                        timedelta(seconds=1))
                    continue

                start_date = (
                    stepping_date and stepping_date[-1] or
                    base_date[0]
                )
                end_date = fields.Datetime.to_string(
                    fields.Datetime.from_string(leave.date_from) -
                    timedelta(seconds=1)
                )
                split_date.append((start_date, end_date))
                stepping_date.append(fields.Datetime.to_string(
                    fields.Datetime.from_string(leave.date_to) +
                    timedelta(seconds=1))
                )

            right_overlapping = self.search([
                ('date_from', '>=', values['date_from']),
                ('date_from', '<', values['date_to']),
                ('date_to', '>', values['date_to']),
                ('employee_id', '=', values['employee_id']),
                ('category_id', '=', values['category_id']),
                ('type', '=', values['type']),
                ('state', 'not in', ['cancel', 'refuse']),
            ], limit=1)

            if right_overlapping:
                base_date[1] = fields.Datetime.to_string(
                    fields.Datetime.from_string(right_overlapping.date_from) -
                    timedelta(seconds=1)
                )
                if stepping_date:
                    split_date.append(stepping_date[-1], base_date[1])
            elif stepping_date and split_date:
                split_date.append((stepping_date[-1], base_date[1]))

            if not split_date:
                split_date.append(base_date)

            for period in split_date:
                new_vals = values.copy()
                new_vals['date_from'] = period[0]
                new_vals['date_to'] = period[1]

                res = super(HrHolidays, self).create(new_vals)
            return res
        return super(HrHolidays, self).create(values)
