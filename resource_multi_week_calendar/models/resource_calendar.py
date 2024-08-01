# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    parent_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        domain=[("parent_calendar_id", "=", False)],
        # TODO: should this cascade instead?
        ondelete="set null",
        string="Main Working Time",
    )
    child_calendar_ids = fields.One2many(
        comodel_name="resource.calendar",
        inverse_name="parent_calendar_id",
        # TODO: this causes a recursion error, but seems correct to me.
        # domain=[("child_calendar_ids", "=", [])],
        string="Alternating Working Times",
        copy=True,
    )
    family_calendar_ids = fields.One2many(
        comodel_name="resource.calendar",
        compute="_compute_family_calendar_ids",
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
    # If this value is not unique, the behaviour is undefined. Fortunately, this
    # should not happen in regular Odoo usage.
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
    current_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        compute="_compute_current_week",
        recursive=True,
    )

    multi_week_epoch_date = fields.Date(
        string="Date of First Week",
        help="""When using alternating weeks, the week which contains the
        specified date becomes the first week, and all subsequent weeks
        alternate in order.""",
        # required=True,
        # default="1970-01-01",
        # Compute this on child calendars; write this manually on parent
        # calendars. Would use 'related=', but that wouldn't work here. Although
        # technically, the value of this field on child calendars isn't super
        # pertinent.
        compute="_compute_multi_week_epoch_date",
        readonly=False,
        store=True,
        recursive=True,
    )

    @api.depends(
        "child_calendar_ids",
        "parent_calendar_id",
        "parent_calendar_id.child_calendar_ids",
    )
    def _compute_family_calendar_ids(self):
        for calendar in self:
            parent = calendar.parent_calendar_id or calendar
            calendar.family_calendar_ids = parent | parent.child_calendar_ids

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
                    start=2,
                ):
                    if calendar == sibling:
                        calendar.week_number = week_number
                        break
            else:
                calendar.week_number = 1

    def _get_first_day_of_epoch_week(self):
        self.ensure_one()
        return self.multi_week_epoch_date - timedelta(
            days=self.multi_week_epoch_date.weekday()
        )

    @api.depends(
        "multi_week_epoch_date",
        "week_number",
        "family_calendar_ids",
        # TODO: current date. Port company_today or add a cron. Or don't store.
    )
    def _compute_current_week(self):
        for calendar in self:
            family_size = len(calendar.family_calendar_ids)
            weeks_since_epoch = math.floor(
                (fields.Date.today() - calendar._get_first_day_of_epoch_week()).days / 7
            )
            current_week_number = (weeks_since_epoch % family_size) + 1
            # TODO: does this work in the negative, too?
            calendar.current_week_number = current_week_number
            calendar.current_calendar_id = calendar.family_calendar_ids.filtered(
                lambda item: item.week_number == current_week_number
            )

    @api.depends("parent_calendar_id.multi_week_epoch_date")
    def _compute_multi_week_epoch_date(self):
        for calendar in self:
            parent = calendar.parent_calendar_id
            if parent:
                calendar.multi_week_epoch_date = parent.multi_week_epoch_date
            else:
                # A default value.
                calendar.multi_week_epoch_date = "1970-01-01"

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

    @api.constrains("parent_calendar_id", "multi_week_epoch_date")
    def _check_epoch_date_matches_parent(self):
        for calendar in self:
            if calendar.parent_calendar_id:
                if (
                    calendar.multi_week_epoch_date
                    != calendar.parent_calendar_id.multi_week_epoch_date
                ):
                    # Because the epoch date is hidden on the views of children,
                    # this should not happen. However, for sanity, we do this
                    # check anyway.
                    raise ValidationError(
                        _(
                            "Working Time '%s' has an epoch date which does not"
                            " match its Main Working Time's. This should not happen."
                        )
                        % calendar.name
                    )
