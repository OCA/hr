from datetime import datetime, time, timedelta

from pytz import timezone

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    is_seasonal = fields.Boolean(
        string="Seasonal Calendar",
        help="When enabled, this calendar has no working hours of its own. "
        "Instead, the working time is taken from the season matching each date, "
        "falling back to the default working time for uncovered dates.",
    )
    season_ids = fields.One2many(
        comodel_name="resource.calendar.season",
        inverse_name="calendar_id",
        string="Seasons",
    )
    default_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Default Working Time",
        ondelete="restrict",
        help="Working time applied on dates not covered by any season.",
    )

    @api.constrains("is_seasonal", "default_calendar_id")
    def _check_seasonal(self):
        for calendar in self:
            if not calendar.is_seasonal:
                continue
            if not calendar.default_calendar_id:
                raise ValidationError(
                    _(
                        "Seasonal calendar %(name)s requires a default working time.",
                        name=calendar.name,
                    )
                )
            if calendar.default_calendar_id.is_seasonal:
                raise ValidationError(
                    _(
                        "The default working time of %(name)s cannot itself be a "
                        "seasonal calendar.",
                        name=calendar.name,
                    )
                )
            if calendar.default_calendar_id == calendar:
                raise ValidationError(
                    _(
                        "Seasonal calendar %(name)s cannot use itself as the default "
                        "working time.",
                        name=calendar.name,
                    )
                )

    def _get_season_calendar(self, day):
        self.ensure_one()
        season = self.season_ids.filtered(lambda s: s._contains_date(day))[:1]
        return season.season_calendar_id or self.default_calendar_id

    def _split_periods_by_season(self, start_dt, end_dt):
        """Split ``[start_dt, end_dt]`` into consecutive sub-periods, each
        mapped to the working-time calendar that applies for its dates."""
        self.ensure_one()
        cal_tz = timezone(self.tz or "UTC")
        start_local = start_dt.astimezone(cal_tz)
        end_local = end_dt.astimezone(cal_tz)
        periods = []
        segment_start = start_dt
        segment_calendar = self._get_season_calendar(start_local.date())
        day = start_local.date() + timedelta(days=1)
        last_day = end_local.date()
        while day <= last_day:
            calendar = self._get_season_calendar(day)
            if calendar != segment_calendar:
                boundary = cal_tz.localize(datetime.combine(day, time.min)).astimezone(
                    start_dt.tzinfo
                )
                if boundary > segment_start:
                    periods.append((segment_start, boundary, segment_calendar))
                    segment_start = boundary
                    segment_calendar = calendar
            day += timedelta(days=1)
        periods.append((segment_start, end_dt, segment_calendar))
        return periods

    def _attendance_intervals_batch(
        self, start_dt, end_dt, resources=None, domain=None, tz=None, lunch=False
    ):
        self.ensure_one()
        if not self.is_seasonal:
            return super()._attendance_intervals_batch(
                start_dt, end_dt, resources, domain, tz, lunch
            )
        combined = {}
        for period_start, period_end, calendar in self._split_periods_by_season(
            start_dt, end_dt
        ):
            if not calendar:
                continue
            sub_result = calendar._attendance_intervals_batch(
                period_start, period_end, resources, domain, tz, lunch
            )
            for resource_id, intervals in sub_result.items():
                if resource_id in combined:
                    combined[resource_id] = combined[resource_id] | intervals
                else:
                    combined[resource_id] = intervals
        return combined
