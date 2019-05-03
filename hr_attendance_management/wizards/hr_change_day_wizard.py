# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class ChangeDayDWizard(models.TransientModel):
    _name = 'hr.change.day.wizard'

    state = fields.Selection([
        ('step1', 'step1'),
        ('step2', 'step2'),
    ], default='step1')
    date_select = fields.Selection(selection='_select_dates')

    @api.model
    def get_due_hours_data(self):
        # Inject due_hours_data into object in order to display date selection
        employee_id = self.env.user.employee_ids
        employee_id.ensure_one()

        date_from = datetime.date.today()
        date_to = date_from

        # Propose dates up to following sunday
        while date_to.weekday() != 6:
            date_to += datetime.timedelta(1)
        date_to += datetime.timedelta(7)

        # Create attendance days up to next sunday for having the due hours
        att_day = self.env['hr.attendance.day']
        att_day_created = att_day
        current_date = date_from

        while current_date <= date_to:
            already_exist = att_day.search([
                ('employee_id', '=', employee_id.id),
                ('date', '=', current_date)
            ])
            if not already_exist:
                att_day_created += att_day.create({
                    'employee_id': employee_id.id,
                    'date': current_date,
                })
            current_date += datetime.timedelta(days=1)

        next_att_days = att_day.search([
            ('date', '>', date_from), ('date', '<=', date_to),
            ('due_hours', '>', 0)
        ])

        dates = next_att_days.mapped('date')
        due_hours = next_att_days.mapped('due_hours')

        data = dict()
        for index, date in enumerate(dates):
            #  only get days with due hours
            if due_hours[index] != 0:
                data[date] = due_hours[index]

        #  delete created att_days
        att_day_created.unlink()
        return data

    @api.model
    def _select_dates(self):
        # orders by date
        def _date_format(_date):
            return fields.Date.from_string(_date).strftime("%A %x")

        data = self._context.get('due_hours_data', {})
        return [(k, _date_format(k)) for k in sorted(data.keys())]

    @api.multi
    def go_to_step2(self):
        self.state = 'step2'
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'due_hours_data': self.get_due_hours_data()}
        }

    @api.multi
    def change_due_hours(self):
        employee_id = self.env['res.users'].browse(self._uid).employee_ids
        data = self._context.get('due_hours_data', {})
        vals = {
            'employee_id': employee_id.id,
            'date1': datetime.date.today(),
            'forced1': data[self.date_select],
            'date2': self.date_select,
            'forced2': 0,
            'user_id': employee_id.parent_id.user_id.id
        }
        self.env['hr.change.day.request'].create(vals)
