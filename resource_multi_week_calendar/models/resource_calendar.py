# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models, _
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

    @api.constrains("parent_calendar_id", "child_calendar_ids")
    def _check_child_is_not_parent(self):
        err_str = _(
            "Working Time '%s' may not be the Main Working Time of another"
            " Working Time ('%s') while it has a Main Working Time itself ('%s')"
        )
        for calendar in self:
            if calendar.parent_calendar_id and calendar.child_calendar_ids:
                raise ValidationError(
                    err_str
                    % (
                        calendar.name,
                        calendar.child_calendar_ids[0].name,
                        calendar.parent_calendar_id.name,
                    )
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
                    % (
                        calendar.parent_calendar_id.name,
                        calendar.name,
                        calendar.parent_calendar_id.parent_calendar_id.name,
                    )
                )
