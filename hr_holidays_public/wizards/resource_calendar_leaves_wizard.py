from datetime import datetime, time
from pytz import timezone, utc

from odoo import api, models, fields


class ResourceCalendarLeavesWizard(models.TransientModel):
    _name = 'public.holidays.resource.calendar.leaves.wizard'
    _description = 'Generate Resource Leaves from Public Holidays'

    def _default_holidays_id(self):
        return self.env['hr.holidays.public'].search([
            ('year', '=', datetime.today().year)])

    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Calendar',
        required=True)
    holidays_id = fields.Many2one(
        comodel_name='hr.holidays.public',
        string='Holidays',
        default=_default_holidays_id,
        required=True)
    replace = fields.Boolean(
        string='Replace Current',
        help='Replace existing global leaves on resource.',
        default=True)

    @api.multi
    def create_leaves(self):
        self.ensure_one()
        leaves = []
        tz = timezone(self.calendar_id.tz)
        for line in self.holidays_id.line_ids:
            dt_from = tz.localize(datetime.combine(line.date, time.min))
            dt_to = tz.localize(datetime.combine(line.date, time.max))
            leaves.append({
                'name': line.name,
                'date_from': dt_from.astimezone(utc),
                'date_to': dt_to.astimezone(utc),
            })
        if self.replace:
            self.calendar_id.global_leave_ids.unlink()
        self.calendar_id.write({
            'leave_ids': [(0, 0, leave) for leave in leaves]
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'resource.calendar',
            'res_id': self.calendar_id.id,
            'view_mode': 'form',
        }
