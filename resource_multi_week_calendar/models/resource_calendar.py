# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.resource.models.resource import Intervals


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    parent_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        domain=[("parent_calendar_id", "=", False)],
        ondelete="cascade",
        string="Main Working Time",
    )
    child_calendar_ids = fields.One2many(
        comodel_name="resource.calendar",
        inverse_name="parent_calendar_id",
        string="Alternating Working Times",
        copy=True,
    )
    # These are all your siblings (including yourself) if you are a child, or
    # all your children if you are a parent. This is not a sorted set.
    multi_week_calendar_ids = fields.One2many(
        comodel_name="resource.calendar",
        compute="_compute_multi_week_calendar_ids",
        recursive=True,
    )
    is_multi_week = fields.Boolean(compute="_compute_is_multi_week", store=True)

    # Making week_number a computed derivative of week_sequence has the
    # advantage of being able to drag calendars around in a table, and not
    # having to manually fiddle with every week number (nor make sure that no
    # weeks are skipped).
    #
    # However, week sequences MUST be unique. Unfortunately, creating a
    # constraint on (parent_calendar_id, week_sequence) does not work. The
    # constraint method is called before all children/siblings are saved,
    # meaning that they can conflict with each other in this interim stage.
    #
    # If this value is not unique, the order is preserved between the identical
    # elements. The elements of child_calendar_ids are always sorted by _order,
    # which is id by default. The value may not be unique when new calendars are
    # added.
    week_sequence = fields.Integer(default=0)
    week_number = fields.Integer(
        compute="_compute_week_number",
        store=True,
        recursive=True,
    )
    current_week_number = fields.Integer(
        compute="_compute_current_week",
        recursive=True,
    )
    current_multi_week_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        compute="_compute_current_week",
        recursive=True,
    )

    multi_week_epoch_date = fields.Date(
        string="Date of First Week",
        help="""When using alternating weeks, the week which contains the
        specified date becomes the first week, and all subsequent weeks
        alternate in order.""",
        required=True,
        default="1970-01-01",
    )

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        sequences = sorted(self.multi_week_calendar_ids.mapped("week_sequence"))
        if sequences:
            # Assign highest value sequence.
            default["week_sequence"] = sequences[-1] + 1
        return super().copy(default=default)

    @api.depends(
        "child_calendar_ids",
        "parent_calendar_id",
        "parent_calendar_id.child_calendar_ids",
    )
    def _compute_multi_week_calendar_ids(self):
        for calendar in self:
            parent = calendar.parent_calendar_id or calendar
            calendar.multi_week_calendar_ids = parent.child_calendar_ids

    @api.depends(
        "child_calendar_ids",
        "parent_calendar_id",
    )
    def _compute_is_multi_week(self):
        for calendar in self:
            calendar.is_multi_week = bool(
                calendar.child_calendar_ids or calendar.parent_calendar_id
            )

    @api.depends(
        "week_sequence",
        "parent_calendar_id",
        "parent_calendar_id.child_calendar_ids",
        "parent_calendar_id.child_calendar_ids.week_sequence",
    )
    def _compute_week_number(self):
        for calendar in self:
            parent = calendar.parent_calendar_id
            if parent:
                for week_number, sibling in enumerate(
                    parent.child_calendar_ids.sorted(lambda item: item.week_sequence),
                    start=1,
                ):
                    if calendar == sibling:
                        calendar.week_number = week_number
                        break
            else:
                # Parent calendars have no week number.
                calendar.week_number = 0

    def _get_first_day_of_epoch_week(self):
        self.ensure_one()
        epoch_date = self.get_multi_week_epoch_date()
        return epoch_date - timedelta(days=epoch_date.weekday())

    def _get_week_number(self, day=None):
        self.ensure_one()
        if not self.is_multi_week:
            return 0
        if day is None:
            day = fields.Date.today()
        if isinstance(day, datetime):
            day = day.date()
        calendar_count = len(self.multi_week_calendar_ids)
        weeks_since_epoch = math.floor(
            (day - self._get_first_day_of_epoch_week()).days / 7
        )
        return (weeks_since_epoch % calendar_count) + 1

    def _get_multi_week_calendar(self, day=None):
        self.ensure_one()
        if not self.is_multi_week:
            return self
        week_number = self._get_week_number(day=day)
        # Should return a 1-item recordset. If it does not, we've hit a bug.
        return self.multi_week_calendar_ids.filtered(
            lambda item: item.week_number == week_number
        )

    @api.depends(
        "multi_week_epoch_date",
        "week_number",
        "multi_week_calendar_ids",
    )
    def _compute_current_week(self):
        for calendar in self:
            current_calendar = calendar._get_multi_week_calendar()
            calendar.current_multi_week_calendar_id = current_calendar
            calendar.current_week_number = current_calendar.week_number

    @api.constrains("parent_calendar_id", "child_calendar_ids")
    def _check_child_is_not_parent(self):
        err_str = _(
            "Working Time '%(name)s' may not be the Main Working Time of"
            " another Working Time ('%(child)s') while it has a Main Working"
            " Time itself ('%(parent)s')"
        )
        for calendar in self:
            if calendar.parent_calendar_id and calendar.child_calendar_ids:
                raise ValidationError(
                    err_str
                    % {
                        "name": calendar.name,
                        "child": calendar.child_calendar_ids[0].name,
                        "parent": calendar.parent_calendar_id.name,
                    }
                )
            # This constraint isn't triggered on calendars which have children
            # added to them. Therefore, we also check whether our parent already
            # has a parent.
            if (
                calendar.parent_calendar_id
                and calendar.parent_calendar_id.parent_calendar_id
            ):
                raise ValidationError(
                    err_str
                    % {
                        "name": calendar.parent_calendar_id.name,
                        "child": calendar.name,
                        "parent": calendar.parent_calendar_id.parent_calendar_id.name,
                    }
                )

    def get_multi_week_epoch_date(self):
        self.ensure_one()
        if self.parent_calendar_id:
            return self.parent_calendar_id.multi_week_epoch_date
        return self.multi_week_epoch_date

    @api.model
    def _split_into_weeks(self, start_dt, end_dt):
        # TODO: This method splits weeks on the timezone of start_dt. Maybe it
        # should split weeks on the timezone of the calendar. It is not
        # immediately clear to me how to implement that.
        current_start = start_dt
        while current_start < end_dt:
            # Calculate the end of the week (Monday 00:00:00, the threshold
            # of Sunday-to-Monday.)
            days_until_monday = 7 - current_start.weekday()
            week_end = current_start + timedelta(days=days_until_monday)
            week_end = week_end.replace(hour=0, minute=0, second=0, microsecond=0)

            current_end = min(week_end, end_dt)
            yield (current_start, current_end)

            # Move to the next week (start of next Monday)
            current_start = current_end

    def _attendance_intervals(self, start_dt, end_dt, resource=None):
        self.ensure_one()
        if not self.is_multi_week:
            return super()._attendance_intervals(start_dt, end_dt, resource=resource)

        calendars_by_week = {
            calendar.week_number: calendar for calendar in self.multi_week_calendar_ids
        }
        result = Intervals()

        # Calculate each week separately, choosing the correct calendar for each
        # week.
        for week_start, week_end in self._split_into_weeks(start_dt, end_dt):
            result |= super(
                ResourceCalendar,
                calendars_by_week[self._get_week_number(week_start)].with_context(
                    # This context is not used here, but could possibly be
                    # used by other modules that use this module. I am not
                    # sure how useful it is.
                    recursive_multi_week=True
                ),
            )._attendance_intervals(week_start, week_end, resource=resource)

        return result
