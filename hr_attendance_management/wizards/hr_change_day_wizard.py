import datetime
from collections import OrderedDict

from odoo import models, fields, api


class ChangeDayDWizard(models.TransientModel):
    _name = 'hr.change.day.wizard'

    @api.multi
    def go_to_step2(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.change.day.wizard.step2',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'data': self.get_next_due_hours()}
        }

    @api.multi
    def get_next_due_hours(self):
        employee_id = self.env['res.users'].browse(self._uid).employee_ids
        employee_id.ensure_one()

        date_from = datetime.date.today()
        date_to = date_from

        while date_to.weekday() != 6:
            date_to += datetime.timedelta(1)
        date_to += datetime.timedelta(7)

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

        next_att_days = att_day.search(
            [('date', '>', date_from), ('date', '<=', date_to)])

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


class ChangeDayWizardStep2(models.TransientModel):
    _name = 'hr.change.day.wizard.step2'

    dates = fields.Selection(selection='_compute_dates')

    @api.multi
    def _compute_dates(self):
        if 'data' in self._context:
            d = self._context['data']
            # orders by date
            return [(k, v) for k, v in OrderedDict(sorted(d.items())).items()]
        return [('default', 'no valid date')]

    @api.multi
    def change_due_hours(self):
        employee_id = self.env['res.users'].browse(self._uid).employee_ids

        vals = {
            'employee_id': employee_id.id,
            'date1': datetime.date.today(),
            'forced1': self._context['data'][self.dates],
            'date2': self.dates,
            'forced2': 0,
            'user_id': employee_id.parent_id.user_id.id
        }
        self.env['hr.change.day.request'].create(vals)
