# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import WEEKLY
from dateutil.tz import gettz, tzutc
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
        start = datetime.datetime.today().replace(tzinfo=tzutc())
        stop = False
        even_odd_occurrences = 0
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
                odd = False
                if rule._interval == 2:
                    occurrences = rule[:2]
                    odd = len(occurrences) == 2 and all(
                        bool(occurrence.isocalendar()[1] % 2)
                        for occurrence in occurrences
                    )
                    even_odd_occurrences += 1

                # allocate this rule to the correct timeslot in the simplified
                # attendance (timeslot = day, morning/afternoon, even/odd week)
                key = (self.env['resource.calendar']._get_afternoon_hour() >
                       attendance.hour_from) and 'morning' or 'afternoon'
                for day in result['data%s' % (odd and '_odd' or '')]:
                    if day['day'] not in rule._byweekday:
                        continue
                    day[key] += attendance.hour_to - attendance.hour_from

        if even_odd_occurrences:
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
            this.attendance_ids = attendances

    @api.multi
    def _attendance_from_simplified(self):
        self.ensure_one()

        # Validate input
        simplified_attendance = self.simplified_attendance
        if not simplified_attendance:
            return []
        attendance_start = simplified_attendance.get('start')
        if not attendance_start:
            return []
        if len(attendance_start) > 10:
            raise ValidationError(_(
                'Only date allowed as start of schedule, not datetime'))
        attendance_stop = simplified_attendance.get('stop')
        if attendance_stop and len(attendance_stop) > 10:
            raise ValidationError(_(
                'Only date allowed as stop of schedule, not datetime'))
        _type = simplified_attendance.get('type', 'null') or 'null'
        if _type == 'null':
            return []
        else:
            odd_even = _type == 'odd'

        # convert the start and stop dates via a naive datetime to
        # UTC datetimes for SerializableRRuleSet
        start_naive = fields.Datetime.from_string(attendance_start)
        start_is_even = not bool(start_naive.isocalendar()[1] % 2)
        tz = gettz(self.env.user.tz or 'utc')
        start = start_naive.replace(tzinfo=tz).astimezone(tzutc())
        stop = False
        if attendance_stop:
            stop_naive = fields.Datetime.from_string(attendance_stop)
            stop = stop_naive.replace(tzinfo=tz).replace(
                hour=23, minute=59).astimezone(tzutc())

        morning_hour = self._get_morning_hour()
        afternoon_hour = self._get_afternoon_hour()
        days_done = set()
        result = []
        rule = self.env['resource.calendar.attendance']._default_rrule()[0]
        for key in ['data'] + (['data_odd'] if odd_even else []):
            for day in simplified_attendance.get(key, ()):
                start_weekday = start_naive.weekday()
                weekday = day.get('day', 0)
                if not odd_even:
                    start_offset = 0
                elif start_is_even and key == 'data_odd':
                    start_offset = 7 - start_weekday  # next week monday
                elif not start_is_even and key == 'data':
                    start_offset = 7 - start_weekday  # next week monday
                elif start_weekday <= weekday:
                    start_offset = 0  # still this week
                else:
                    start_offset = 14 - start_weekday  # overnext monday
                day_rule = dict(
                    rule, byweekday=[weekday],
                    interval=2 if odd_even else 1,
                    dtstart=fields.Datetime.to_string(
                        start + relativedelta(days=start_offset)),
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
        end_dt = self.env.context.get('end_dt_res_calendar')
        start_dt_utc = None
        end_dt_utc = None
        current_tz = gettz(self.env.user.tz or 'utc')
        if start_dt:
            start_dt = start_dt.replace(
                hour=0, minute=0, second=0, microsecond=0)
            start_dt_utc = start_dt.replace(tzinfo=current_tz).astimezone(
                tzutc()).replace(tzinfo=None)
        if end_dt:
            end_dt = end_dt.replace(
                hour=23, minute=59, second=59, microsecond=0)
            end_dt_utc = end_dt.replace(tzinfo=current_tz).astimezone(
                tzutc()).replace(tzinfo=None)

        # Filter attendances
        interval = None
        attendances = []
        for i, attendance in enumerate(self.browse(id).attendance_ids):
            occurrence = None
            if attendance.rrule:

                # Filter out attendances that dont occur in [start_dt, end_dt]
                if start_dt and end_dt:
                    occurrence = attendance.rrule.between(
                        start_dt_utc,
                        end_dt_utc,
                        inc=True
                    )
                elif start_dt:
                    occurrence = attendance.rrule.after(start_dt_utc, inc=True)
                elif end_dt:
                    occurrence = attendance.rrule.before(end_dt_utc, inc=True)

                # Set interval
                rrule_dtstart = attendance.rrule._rrule[0]._dtstart
                if rrule_dtstart:
                    rrule_start = rrule_dtstart.replace(tzinfo=None)
                    interval = (
                        rrule_start,
                        rrule_start + datetime.timedelta(days=14),
                    )

            # Fallback check on weekday
            if (start_dt or end_dt) and not occurrence:
                continue
            if not interval:
                interval = self._get_check_interval()
            if not any(date.weekday() in weekdays
                       for date, _ in
                       attendance._iter_rrule(*interval)):
                continue

            attendances.append(attendance)

        return attendances

    @api.multi
    def get_weekdays(self, default_weekdays=None):
        """ Check each attendance in its own first two weeks """
        if not self:
            return super(ResourceCalendar, self).get_weekdays(
                default_weekdays=default_weekdays
            )
        weekdays = set()
        for attendance in self[:1].attendance_ids:
            if attendance.rrule:
                rrule_dtstart = attendance.rrule._rrule[0]._dtstart
                rrule_start = rrule_dtstart.replace(tzinfo=None)
                interval = (
                    rrule_start,
                    rrule_start + datetime.timedelta(days=14),
                )
            else:
                interval = self._get_check_interval()
            for date, _dummy in attendance._iter_rrule(*interval):
                weekdays.add(date.weekday())
        return list(weekdays)

    @api.model
    def _get_check_interval(self):
        """for some computations, we need to generate some dates and inspect
        the result. By overriding this function you can change the interval
        used in case the default week from no doesn't work for you"""
        dt = datetime.datetime.now()
        return dt, dt + datetime.timedelta(days=7)

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
        # Needed because _schedule_days does not pass end_dt to
        # get_working_intervals_of_day.
        if ctx.get('came_from_schedule_days') and start_dt:
            end_of_day = start_dt.replace(hour=23, minute=59, second=59)
            ctx.update({'end_dt_res_calendar': end_of_day})
        return super(ResourceCalendar, self).get_working_intervals_of_day(
            cr, uid, id, start_dt=start_dt, end_dt=end_dt, leaves=leaves,
            compute_leaves=compute_leaves, resource_id=resource_id,
            default_interval=default_interval, context=ctx)

    def _schedule_days(self, cr, uid, id, days, day_date=None,
                       compute_leaves=False, resource_id=None,
                       default_interval=None, context=None):
        # Signal get_working_intervals_of_day to calculate end_dt from start_dt
        ctx = dict(context or {})
        ctx.update({'came_from_schedule_days': True})
        return super(ResourceCalendar, self)._schedule_days(
            cr, uid, id, days, day_date=day_date,
            compute_leaves=compute_leaves, resource_id=resource_id,
            default_interval=default_interval, context=ctx)
