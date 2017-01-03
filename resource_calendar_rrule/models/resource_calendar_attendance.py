# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import pytz
from dateutil import rrule
from openerp import api, fields, models
try:
    from openerp.addons.field_rrule import FieldRRule
except ImportError:
    FieldRRule = fields.Serialized


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    rrule = FieldRRule(
        'Repetition', help='Add an arbitrary amount of repetition rules.',
        required=True, default=lambda self: self._default_rrule(),
        stable_times=True,
    )
    rrule_preview = fields.Text('Preview', compute='_compute_rrule_preview')

    @api.model
    def create(self, vals):
        # if some legacy code creates an attendance, set up a repetition rule
        # for it
        if 'rrule' not in vals and 'dayofweek' in vals:
            rrule = self._default_rrule()
            rrule[0]['byweekday'] = [vals['dayofweek']]
            vals['rrule'] = rrule
        return super(ResourceCalendarAttendance, self).create(vals)

    @api.multi
    def _compute_rrule_preview(self):
        language = self.env['res.lang'].search([
            ('code', '=', self.env.context.get('lang', self.env.user.lang))
        ])
        for this in self:
            text = ''
            for start, end in this._iter_rrule(
                    datetime.datetime.now(),
                    datetime.datetime.now() + datetime.timedelta(days=7),
            ):
                text += '%s %s - %s\n' % (
                    fields.Datetime.context_timestamp(this, start)
                    .strftime(language.date_format),
                    fields.Datetime.context_timestamp(this, start)
                    .strftime(language.time_format),
                    fields.Datetime.context_timestamp(this, end)
                    .strftime(language.time_format),
                )
            this.rrule_preview = text

    @api.model
    def _default_rrule(self):
        return [{
            'freq': rrule.WEEKLY,
            'type': 'rrule',
            'interval': 1,
            'byweekday': [0, 1, 2, 3, 4],
            'dtstart': fields.Date.context_today(self),
        }]

    @api.multi
    def _iter_rrule(self, start, stop, include=True):
        """get an iterator through our rule yielding interval tuples"""
        self.ensure_one()
        for date in self.rrule().between(start, stop, inc=include):
            date = fields.Datetime.context_timestamp(self, date)
            yield (
                date.replace(
                    hour=int(self.hour_from),
                    minute=int(self.hour_from % 1 * 60)
                ).astimezone(pytz.utc).replace(tzinfo=None),
                date.replace(
                    hour=int(self.hour_to),
                    minute=int(self.hour_to % 1 * 60)
                ).astimezone(pytz.utc).replace(tzinfo=None),
            )
