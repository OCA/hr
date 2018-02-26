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
            self._adapt_start_until_from_vals(rrule[0], vals)
            vals['rrule'] = rrule
        return super(ResourceCalendarAttendance, self).create(vals)

    @api.multi
    def write(self, vals):
        result = super(ResourceCalendarAttendance, self).write(vals)
        if 'date_from' in vals or 'date_to' in vals or 'dayofweek' in vals:
            for this in self.filtered('rrule'):
                rrule = []
                for rule in this.rrule:
                    if rule['type'] != 'rrule':
                        rrule.append(rule)
                        continue
                    rule = dict(rule)
                    self._adapt_start_until_from_vals(rule, vals)
                    rrule.append(rule)
                this.write({'rrule': rrule})
        return result

    @api.model
    def _adapt_start_until_from_vals(self, rule, vals):
        if vals.get('date_from'):
            rule['dtstart'] = fields.Datetime.to_string(
                (
                    isinstance(vals['date_from'], datetime.datetime) and
                    vals['date_from'] or
                    fields.Datetime.from_string(vals['date_from'])
                ).replace(hour=0, minute=0, second=0)
            )
        elif 'date_from' in vals:
            rule['dtstart'] = None
        if vals.get('date_to'):
            rule['until'] = fields.Datetime.to_string(
                (
                    isinstance(vals['date_to'], datetime.datetime) and
                    vals['date_to'] or
                    fields.Datetime.from_string(vals['date_to'])
                ).replace(hour=23, minute=59, second=59)
            )
        elif 'date_to' in vals:
            rule['until'] = None
        if vals.get('dayofweek'):
            rule['byweekday'] = [vals['dayofweek']]

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
        start = max(
            fields.Datetime.from_string(self.date_from) or start, start
        )
        stop = min(fields.Datetime.from_string(self.date_to) or stop, stop)
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
