# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.rrule import WEEKLY
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_is_zero, float_round


DEFAULT_MORNING_HOUR = 8.0
DEFAULT_AFTERNOON_HOUR = 13.0
DEFAULT_MAX_HOURS_PER_DAY = 12.0


def _hours_per_day(data):
    """ helper function to get the total hours per day """
    return data.get('morning', 0.0) + data.get('afternoon', 0.0)


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    simplified_attendance = fields.Serialized(
        'Working time', compute='_compute_simplified_attendance',
        inverse='_inverse_simplified_attendance',
        default=lambda self: self._default_simplified_attendance(),
    )

    @api.model
    def _get_morning_hour(self):
        """ Hour of the day at which the morning schedule starts """
        return float(self.env['ir.config_parameter'].get_param(
            'resource_calendar_rrule.simplified_morning',
            DEFAULT_MORNING_HOUR,
        ))

    @api.model
    def _get_afternoon_hour(self):
        """ Hour of the day at which the afternoon schedule starts """
        return float(self.env['ir.config_parameter'].get_param(
            'resource_calendar_rrule.simplified_afternoon',
            DEFAULT_AFTERNOON_HOUR,
        ))

    @api.model
    def _get_max_hours_per_day(self):
        """ Max hours per day allowed in the schedule """
        return float(self.env['ir.config_parameter'].get_param(
            'resource_calendar_rrule.max_hours_per_day',
            DEFAULT_MAX_HOURS_PER_DAY,
        ))

    def _validate_simplified_attendance(self, attendance):
        """ Sanity check for attendance hours """
        to_check = list(attendance.get('data', []))
        if attendance.get('type') == 'odd':
            to_check += attendance.get('data_odd', [])
        for day in to_check:
            _max = self._get_max_hours_per_day()
            if _hours_per_day(day) > _max:
                raise ValidationError(
                    _("The max per day cannot exceed %.01f hours. "
                      "(You can set this lower or higher with the "
                      "'resource_calendar_rrule.max_hours_per_day' "
                      "configuration parameter.)") % (_max,))
            if self._get_afternoon_hour() + day.get('afternoon', 0.0) >= 24.0:
                raise ValidationError(
                    _('Afternoon shift cannot go past midnight.'))

    @api.multi
    def write(self, values):
        to_delete = []
        if 'simplified_attendance' in values:
            attendance = values['simplified_attendance']
            self._validate_simplified_attendance(attendance)
            to_delete.extend(self.mapped('attendance_ids').ids)
        ret = super(ResourceCalendar, self).write(values)
        self.env['resource.calendar.attendance'].browse(to_delete).unlink()
        return ret

    def _default_simplified_attendance(self):
        return {
            'type': 'all',
            'data': [dict(day=day, morning=4, afternoon=4)
                     for day in range(5)],
            'start': fields.Date.today(),
            'stop': False,
        }

    @api.multi
    def _compute_simplified_attendance(self):
        for this in self:
            this.simplified_attendance = this\
                ._simplified_from_attendances()

    @api.multi
    @api.depends('attendance_ids')
    def _simplified_from_attendances(self, attendances=None):
        self.ensure_one()
        if not attendances:
            attendances = self.attendance_ids
        result = {'type': 'all', 'data': [], 'data_odd': []}
        for day in range(7):
            result['data'].append(dict(day=day, morning=0, afternoon=0))
            result['data_odd'].append(dict(day=day, morning=0, afternoon=0))
        if not attendances:
            result['type'] = 'null'
        warn = ''
        start = datetime.datetime.today().replace(tzinfo=pytz.utc)
        stop = False
        even_odd_occurrences = set()
        for attendance in attendances:
            for rule in attendance.rrule._rrule:
                if rule._byeaster or rule._bymonth or rule._bymonthday or\
                        rule._byyearday or rule._interval not in [1, 2] or\
                        rule._freq != WEEKLY or not rule._dtstart:
                    # TODO: warn if the rrule can't be simplified
                    warn += _('Ignoring %s') % rule
                    continue

                if rule._dtstart < start:
                    start = rule._dtstart
                if rule._until and (not stop or stop > rule._until):
                    stop = rule._until

                # This piece of code is meant to detect if this is an rrule
                # implementing the simplified occurrence only for odd weeks.
                # It looks two consecutive occurrences. If both are odd weeks,
                # we know that this is a rule for odd weeks. Otherwise, there
                # would be an even week in between.
                odd = all(
                    bool(occurrence.isocalendar()[1] % 2)
                    for occurrence in rule[:2]
                )
                even_odd_occurrences.add('odd' if odd else 'even')

                # allocate this rule to the correct timeslot in the simplified
                # attendance (timeslot = day, morning/afternoon, even/odd week)
                key = (self.env['resource.calendar']._get_afternoon_hour() >
                       attendance.hour_from) and 'morning' or 'afternoon'
                for day in result['data%s' % (odd and '_odd' or '')]:
                    if day['day'] not in rule._byweekday:
                        continue
                    day[key] += attendance.hour_to - attendance.hour_from

        if 'odd' in even_odd_occurrences:
            result['type'] = 'odd'
        result.update(
            start=fields.Date.to_string(start),
            stop=fields.Date.to_string(stop),
        )
        return result

    @api.multi
    def _inverse_simplified_attendance(self):
        for this in self:
            attendances = this._attendance_from_simplified()
            # this.attendance_ids.unlink()
            this.attendance_ids = attendances

    @api.multi
    def _attendance_from_simplified(self):
        self.ensure_one()
        simplified_attendance = self.simplified_attendance
        if not simplified_attendance:
            return []
        attendance_start = simplified_attendance.get('start')
        if not attendance_start:
            return []
        attendance_stop = simplified_attendance.get('stop')
        _type = simplified_attendance.get('type', 'null') or 'null'
        if _type == 'null':
            return []
        else:
            odd_even = _type == 'odd'
        result = []
        rule = self.env['resource.calendar.attendance']._default_rrule()[0]
        start = fields.Datetime.from_string(attendance_start)
        start_is_even = not bool(start.isocalendar()[1] % 2)
        stop = fields.Datetime.from_string(attendance_stop)
        morning_hour = self._get_morning_hour()
        afternoon_hour = self._get_afternoon_hour()
        days_done = set()
        for key in ['data'] + (['data_odd'] if odd_even else []):
            for day in simplified_attendance.get(key, ()):
                weekday = day.get('day', 0)
                odd_offset = relativedelta(
                    weeks=1
                    if odd_even and (
                        start_is_even and key == 'data_odd' or
                        not start_is_even and key == 'data'
                    )
                    else 0
                )
                day_rule = dict(
                    rule, byweekday=[weekday],
                    interval=2 if odd_even else 1,
                    dtstart=fields.Datetime.to_string(start + odd_offset),
                    until=fields.Datetime.to_string(stop)
                )
                morning_hours = day.get('morning', 0.0)
                afternoon_hours = day.get('afternoon', 0.0)
                if not float_is_zero(morning_hours, precision_digits=2) or \
                        weekday not in days_done:
                    result.append((0, 0, {
                        'name': _('Simplified attendance %s morning') %
                        self.env['resource.calendar.attendance']
                        ._fields['dayofweek'].selection[day['day']][1],
                        'rrule': [day_rule],
                        'date_from': start,
                        'hour_from': morning_hour,
                        'hour_to': morning_hour + float_round(
                            morning_hours, precision_digits=2)
                    }))
                if not float_is_zero(afternoon_hours, precision_digits=2) or \
                        weekday not in days_done:
                    result.append((0, 0, {
                        'name': _('Simplified attendance %s afternoon') %
                        self.env['resource.calendar.attendance']
                        ._fields['dayofweek'].selection[day['day']][1],
                        'rrule': [day_rule],
                        'date_from': start,
                        'hour_from': afternoon_hour,
                        'hour_to': afternoon_hour + float_round(
                            afternoon_hours, precision_digits=2)
                    }))
                days_done.add(weekday)
        return result

    @api.model
    def get_attendances_for_weekdays(self, id, weekdays):
        """ A rewrite of this function """

        start_dt = self.env.context.get('start_dt_res_calendar')
        if start_dt:
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
        end_dt = self.env.context.get('end_dt_res_calendar')
        if end_dt:
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Filter attendances
        attendances = []
        for attendance in self.browse(id).attendance_ids:
            if attendance.rrule:
                tz = pytz.timezone(attendance.rrule.tz)
                # Filter out attendances that dont occur in our date range
                rrule_dtstart = attendance.rrule._rrule[0]._dtstart
                rrule_until = attendance.rrule._rrule[0]._until
                if rrule_dtstart and end_dt:
                    end_dt_tz = end_dt.replace(tzinfo=tz)
                    if rrule_dtstart > end_dt_tz:
                        continue
                if rrule_until and start_dt:
                    start_dt_tz = start_dt.replace(tzinfo=tz)
                    if rrule_until < start_dt_tz:
                        continue
                # Determine interval to check for weekdays
                rrule_start = attendance.rrule[0]
                interval = (
                    rrule_start,
                    rrule_start + datetime.timedelta(days=7),
                )
            else:
                interval = self._get_check_interval()
            # Filter out attendances that dont occur on our chosen weekdays
            if not any(date.weekday() in weekdays
                       for date, _ in attendance._iter_rrule(*interval)):
                continue
            attendances.append(attendance)

        return attendances

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

    def interval_remove_leaves(self, interval, leave_intervals):
        """ Some installations use negative intervals, support them """
        if interval and interval[0] > interval[1]:
            flipped_interval = [interval[1], interval[0]]
            intervals = super(ResourceCalendar, self).interval_remove_leaves(
                flipped_interval, leave_intervals)
            return [(i[1], i[0]) for i in intervals]
        else:
            return super(ResourceCalendar, self).interval_remove_leaves(
                interval, leave_intervals)

    def get_working_intervals_of_day(self, cr, uid, id, start_dt=None,
                                     end_dt=None, leaves=None,
                                     compute_leaves=False, resource_id=None,
                                     default_interval=None, context=None):
        ctx = dict(context or {})
        ctx.update({
            'start_dt_res_calendar': start_dt,
            'end_dt_res_calendar': end_dt,
        })
        return super(ResourceCalendar, self).get_working_intervals_of_day(
            cr, uid, id, start_dt=start_dt, end_dt=end_dt, leaves=leaves,
            compute_leaves=compute_leaves, resource_id=resource_id,
            default_interval=default_interval, context=ctx)
