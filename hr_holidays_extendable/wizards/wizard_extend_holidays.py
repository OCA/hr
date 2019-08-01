# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.hr_holidays.models.hr_holidays import HOURS_PER_DAY


class WizardExtendHolidays(models.TransientModel):

    _name = 'wizard.extend.holidays'

    name = fields.Char()

    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', readonly=True,
    )

    date_from = fields.Datetime(readonly=True,)
    date_to = fields.Datetime()

    number_of_days_temp = fields.Float(
        compute='_compute_number_of_days_temp',
    )

    holidays_id = fields.Many2one(
        comodel_name='hr.holidays'
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            holiday = self.env['hr.holidays'].browse(active_id)
            rec.update({
                'holidays_id': holiday.id,
                'employee_id': holiday.employee_id.id,
                'date_from': holiday.date_from,
                'date_to': holiday.date_to,
                'number_of_days_temp': holiday.number_of_days_temp,
            })
        return rec

    @api.depends('date_to')
    def _compute_number_of_days_temp(self):
        date_from = self.date_from
        date_to = self.date_to

        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self.holidays_id._get_number_of_days(
                date_from, date_to, self.employee_id.id
            ) + self.holidays_id.number_of_days_temp
        else:
            self.number_of_days_temp = 0

    @api.constrains('date_to')
    def _check_date_to_increased(self):
        for record in self:
            if record.date_to < record.holidays_id.date_to:
                raise ValidationError(_('You must extend the holidays'))

    @api.multi
    def extend_holidays(self):
        self.holidays_id.write({
            'date_to': self.date_to,
            'number_of_days_temp': self.number_of_days_temp,
        })
        self.holidays_id._compute_number_of_days()
        self.holidays_id._remove_resource_leave()
        self.holidays_id._create_resource_leave()

        self.holidays_id.meeting_id.write({
            'name': self.holidays_id.display_name,
            'stop': self.date_to,
            'duration': self.number_of_days_temp * HOURS_PER_DAY,
        })

        action = {
            'type': 'ir.actions.act_window',
            'name': self.holidays_id.display_name,
            'res_model': 'hr.holidays',
            'res_id': self.holidays_id.id,
            'view_mode': 'form',
        }
        return action
