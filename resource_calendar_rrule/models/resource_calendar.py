# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.rrule import WEEKLY
from openerp import _, api, fields, models

DEFAULT_MORNING_HOUR = 8.0
DEFAULT_AFTERNOON_HOUR = 13.0


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    simplified_attendance = fields.Serialized(
        'Working time', compute='_compute_simplified_attendance',
        inverse='_inverse_simplified_attendance',
        default=lambda self: self._default_simplified_attendance(),
    )

    def _default_simplified_attendance(self):
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
                if day['morning']:
                    result.append(
                        (0, 0, {
                            'name': _('Simplified attendance %s morning') %
                            self.env['resource.calendar.attendance']
                            ._fields['dayofweek'].selection[day['day']][1],
                            'rrule': [day_rule],
                            'hour_from': morning_hour,
                            'hour_to': morning_hour + day['morning'],
                        })
                    )
                if day['afternoon']:
                    result.append(
                        (0, 0, {
                            'name': _('Simplified attendance %s afternoon') %
                            self.env['resource.calendar.attendance']
                            ._fields['dayofweek'].selection[day['day']][1],
                            'rrule': [day_rule],
                            'hour_from': afternoon_hour,
                            'hour_to': afternoon_hour + day['afternoon'],
                        })
                    )
        return result

    @api.model
    def get_attendances_for_weekdays(self, id, weekdays):
        return [
            attendance
            for attendance in self.browse(id).attendance_ids
            if any(
                date.weekday() in weekdays
                for date, _ in attendance._iter_rrule(
                    *self._get_check_interval()
                )
            )
        ]

    @api.model
    def get_weekdays(self, id, default_weekdays=None):
        if id is None:
            return super(ResourceCalendar, self).get_weekdays(
                default_weekdays=default_weekdays
            )
        return list(set(
            date.weekday()
            for attendance in self.browse(id).attendance_ids
            for date, _ in attendance._iter_rrule(
                *self._get_check_interval()
            )
        ))

    @api.model
    def _get_check_interval(self):
        """for some computations, we need to generate some dates and inspect
        the result. By overriding this function you can change the interval
        used in case the default week from no doesn't work for you"""
        return (
            datetime.datetime.now(),
            datetime.datetime.now() + datetime.timedelta(days=7),
        )
