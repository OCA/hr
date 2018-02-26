# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.rrule import WEEKLY
from odoo import _, api, exceptions, fields, models, tools

DEFAULT_MORNING_HOUR = 8.0
DEFAULT_AFTERNOON_HOUR = 13.0


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    simplified_attendance = fields.Serialized(
        'Working time', compute='_compute_simplified_attendance',
        inverse='_inverse_simplified_attendance',
    )

    @api.model
    def default_simplified_attendance(self):
        result = {
            'type': 'all',
            'data': [],
            'start': fields.Date.today(),
            'stop': False,
        }
        for day in [0, 1, 2, 3, 4]:
            result['data'].extend([
                {
                    'day': day,
                    'morning': 4,
                    'afternoon': 4,
                },
            ])
        return result

    @api.multi
    def _compute_simplified_attendance(self):
        for this in self:
            for attendance in this.attendance_ids:
                this.simplified_attendance = this\
                    ._simplified_from_attendances()

    @api.model
    @api.depends('attendance_ids')
    def _simplified_from_attendances(self):
        self.ensure_one()
        result = {'type': 'all', 'data': [], 'data_odd': []}
        for day in [0, 1, 2, 3, 4, 5, 6]:
            result['data'].append({
                'day': day,
                'morning': 0,
                'afternoon': 0,
            })
            result['data_odd'].append({
                'day': day,
                'morning': 0,
                'afternoon': 0,
            })
        warn = ''
        start = datetime.datetime.today().replace(tzinfo=pytz.utc)
        stop = False
        for attendance in self.attendance_ids:
            for rule in attendance.rrule._rrule:
                if rule._byeaster or rule._bymonth or rule._bymonthday or\
                        rule._byyearday or rule._interval not in [1, 2] or\
                        rule._freq != WEEKLY or not rule._dtstart:
                    # TODO: this neds to warn somehow if the rrule can't be
                    # simplified
                    warn += _('Ignoring %s') % rule
                    continue

                if rule._dtstart < start:
                    start = rule._dtstart
                if rule._until and (not stop or stop > rule._until):
                    stop = rule._until

                odd = all(
                    bool(rule._dtstart.isocalendar()[1] % 2)
                    for occurrence in rule[:2]
                )
                key = float(self.env['ir.config_parameter'].get_param(
                    'resource_calendar_rrule.simplified_afternoon',
                    DEFAULT_AFTERNOON_HOUR,
                )) > attendance.hour_from and 'morning' or 'afternoon'

                for day in result['data%s' % (odd and '_odd' or '')]:
                    if day['day'] not in rule._byweekday:
                        continue
                    day[key] += attendance.hour_to - attendance.hour_from
            for exdate in attendance.rrule._exdate:
                result.setdefault('exdate', [])
                result['exdate'].append(fields.Date.to_string(exdate))
            for rdate in attendance.rrule._rdate:
                result.setdefault('rdate', [])
                result['rdate'].append(fields.Date.to_string(rdate))

        def sum_all(x):
            return x['morning'] + x['afternoon']

        if not sum(map(sum_all, result['data'])):
            result['data'] = result['data_odd']
            result.pop('data_odd')
        elif not sum(map(sum_all, result['data_odd'])):
            result.pop('data_odd')
        else:
            result['type'] = 'odd'
        result.update(
            start=fields.Date.to_string(start),
            stop=fields.Date.to_string(stop),
        )
        if 'rdate' in result:
            result['rdate'] = sorted(set(result['rdate']))
        if 'exdate' in result:
            result['exdate'] = sorted(set(result['exdate']))
        return result

    @api.multi
    def _inverse_simplified_attendance(self):
        for this in self:
            attendances = self._attendance_from_simplified()
            this.attendance_ids.unlink()
            this.attendance_ids = attendances

    @api.multi
    def _attendance_from_simplified(self):
        self.ensure_one()
        simplified_attendance = self.simplified_attendance
        result = []
        rule = self.env['resource.calendar.attendance']._default_rrule()[0]
        start = fields.Datetime.from_string(simplified_attendance['start'])
        start_is_even = not bool(start.isocalendar()[1] % 2)
        odd_even = simplified_attendance['type'] == 'odd'
        morning_hour = float(self.env['ir.config_parameter'].get_param(
            'resource_calendar_rrule.simplified_morning',
            DEFAULT_MORNING_HOUR,
        ))
        afternoon_hour = float(self.env['ir.config_parameter'].get_param(
            'resource_calendar_rrule.simplified_afternoon',
            DEFAULT_AFTERNOON_HOUR,
        ))
        for key in ['data'] + (['data_odd'] if odd_even else []):
            for day in simplified_attendance[key]:
                day_rule = dict(
                    rule, byweekday=[day['day']],
                    interval=2 if odd_even else 1,
                    dtstart=fields.Datetime.to_string(
                        start + relativedelta(
                            weeks=1
                            if odd_even and (
                                start_is_even and key == 'data_odd' or
                                not start_is_even and key == 'data'
                            )
                            else 0
                        )
                    )
                )
                exdate = map(
                    lambda x: {'type': 'exdate', 'date': x},
                    simplified_attendance.get('exdate', [])
                )
                rdate = map(
                    lambda x: {'type': 'rdate', 'date': x},
                    simplified_attendance.get('rdate', [])
                )
                if day['morning']:
                    if morning_hour + day['morning'] > 24:
                        raise exceptions.ValidationError(_(
                            '%.2d + %.2d is more than 24h, you seem to fill '
                            'in times instead an amount of hours'
                        ) % (morning_hour, day['morning']))
                    result.append(
                        (0, 0, {
                            'name': _('Simplified attendance %s morning') %
                            self.env['resource.calendar.attendance']
                            ._fields['dayofweek'].selection[day['day']][1],
                            'rrule': [day_rule] + exdate + rdate,
                            'hour_from': morning_hour,
                            'hour_to': morning_hour + day['morning'],
                        })
                    )
                if day['afternoon']:
                    if afternoon_hour + day['afternoon'] > 24:
                        raise exceptions.ValidationError(_(
                            '%02d + %02d is more then 24h, you seem to fill '
                            'in times instead an amount of hours'
                        ) % (afternoon_hour, day['afternoon']))
                    result.append(
                        (0, 0, {
                            'name': _('Simplified attendance %s afternoon') %
                            self.env['resource.calendar.attendance']
                            ._fields['dayofweek'].selection[day['day']][1],
                            'rrule': [day_rule] + exdate + rdate,
                            'hour_from': afternoon_hour,
                            'hour_to': afternoon_hour + day['afternoon'],
                        })
                    )
        return result

    @api.multi
    @tools.ormcache('self.ids', 'day_dt')
    def get_attendances_for_weekday(self, day_dt):
        return sum((
            self.env['resource.calendar.attendance'].new({
                'name': attendance.name,
                'dayofweek': str(day_dt.weekday()),
                'hour_from': attendance.hour_from,
                'hour_to': attendance.hour_to,
                'date_from': attendance.date_from,
                'date_to': attendance.date_to,
            })
            for attendance in self.mapped('attendance_ids')
            if (
                not attendance.date_from or
                fields.Date.from_string(attendance.date_from) <=
                day_dt.date()
            ) and (
                not attendance.date_to or
                fields.Date.from_string(attendance.date_to) >=
                day_dt.date()
            ) and any(
                date1.weekday() == day_dt.weekday() or
                date2.weekday() == day_dt.weekday()
                for date1, date2 in attendance._iter_rrule(
                    *self._get_check_interval(
                        fields.Datetime.from_string(
                            attendance.date_from or
                            fields.Datetime.to_string(day_dt)
                        ),
                        fields.Datetime.from_string(
                            attendance.date_to and
                            attendance.date_to + ' 23:59:59' or None
                        )
                    )
                )
            )
        ), self.env['resource.calendar.attendance'])

    @api.multi
    @tools.ormcache('self.ids', 'tuple(default_weekdays or [])')
    def get_weekdays(self, default_weekdays=None):
        if not self:
            return super(ResourceCalendar, self).get_weekdays(
                default_weekdays=default_weekdays
            )
        weekdays = set()
        for attendance in self.attendance_ids:
            if attendance.rrule:
                rrule_dtstart = attendance.rrule._rrule[0]._dtstart
                rrule_start = rrule_dtstart.replace(tzinfo=None)
                interval = (
                    rrule_start,
                    rrule_start + datetime.timedelta(days=7),
                )
            else:
                interval = self._get_check_interval()
            for date, dummy in attendance._iter_rrule(*interval):
                weekdays.add(date.weekday())
        return list(weekdays)

    @api.model
    def _get_check_interval(self, default_start=None, default_stop=None):
        """for some computations, we need to generate some dates and inspect
        the result. By overriding this function you can change the interval
        used in case the default week from now doesn't work for you"""
        return (
            default_start or datetime.datetime.now(),
            default_stop or
            datetime.datetime.now() + datetime.timedelta(days=7),
        )
