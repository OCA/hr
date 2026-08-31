# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021-2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    active = fields.Boolean(default=True)
    auto_generate = fields.Boolean()
    employee_ids = fields.One2many(
        "hr.employee",
        "resource_calendar_id",
    )
    employee_calendar_ids = fields.One2many("hr.employee.calendar", "calendar_id")
    # flexible_hours compatibility
    # For the flexible_hours, full_time_required_hours, and hours_per_day fields
    # to function correctly, you must create three fields:
    # - stored_flexible_hours: This field will behave the same as the flexible_hours
    # field
    # - stored_full_time_required_hours: This field will behave the same as the
    # full_time_required_hours field
    # - stored_hours_per_day: This will behave the same as the hours_per_day field
    # The flexible_hour and full_time_required_hours fields are converted to compute
    # fields with store=False to ensure the correct stored_* field is used, except
    # when the calendar is auto_generated and dates are passed via context; in that
    # case, the appropriate value will be defined.
    stored_flexible_hours = fields.Boolean(
        compute="_compute_stored_flexible_hours",
        store=True,
        help="When enabled, it will allow employees to work flexibly, without relying"
        " on the company's working schedule (working hours).",
    )
    stored_full_time_required_hours = fields.Float(
        compute="_compute_stored_full_time_required_hours",
        store=True,
        help="Number of hours to work on the company schedule to be considered as"
        " fulltime.",
    )
    stored_hours_per_day = fields.Float(
        compute="_compute_stored_hours_per_day",
        store=True,
        digits=(2, 2),
        readonly=False,
        help="Average hours per day a resource is supposed to work with this calendar.",
    )
    # We set the field to store=False; we want it to be computed whenever that data
    # needs to be accessed.
    flexible_hours = fields.Boolean(store=False)
    full_time_required_hours = fields.Float(store=False)
    hours_per_day = fields.Float(store=False)

    @api.depends("schedule_type")
    def _compute_stored_flexible_hours(self):
        """Same behavior as the flexible_hours field"""
        for calendar in self:
            calendar.stored_flexible_hours = calendar.schedule_type == "flexible"

    @api.depends(
        "auto_generate",
        "employee_ids.calendar_ids",
        "employee_ids.calendar_ids.calendar_id.stored_flexible_hours",
    )
    @api.depends_context(
        "flexible_hours_from_date",
        "flexible_hours_to_date",
    )
    def _compute_flexible_hours(self):
        """The value of stored_flexible_hours is defined unless the calendar is
        auto_generate; in that case, the hours for the applicable calendars will
        be defined based on the dates specified by context.
        """
        for item in self:
            flexible_hours = item.stored_flexible_hours
            if item.auto_generate:
                from_date = self.env.context.get("flexible_hours_from_date")
                to_date = self.env.context.get("flexible_hours_to_date")
                employee = item.employee_ids[:1]
                if (from_date or to_date) and employee:
                    calendars = employee._get_planning_calendars(from_date, to_date)
                    flexible_hours = (
                        any(c.stored_flexible_hours for c in calendars.calendar_id)
                        if calendars
                        else False
                    )
            item.flexible_hours = flexible_hours

    @api.depends(
        "auto_generate",
        "flexible_hours",
        "employee_ids.calendar_ids",
        "employee_ids.calendar_ids.calendar_id.stored_flexible_hours",
        "employee_ids.calendar_ids.calendar_id.stored_full_time_required_hours",
    )
    @api.depends_context(
        "flexible_hours_from_date",
        "flexible_hours_to_date",
    )
    def _compute_full_time_required_hours(self):
        """The value of full_time_required_hours is defined unless the calendar is
        auto_generate; in that case, the hours for the applicable calendars will
        be defined based on the dates specified by context.
        """
        for item in self:
            hours = item.stored_full_time_required_hours
            if item.auto_generate and item.flexible_hours:
                from_date = self.env.context.get("flexible_hours_from_date")
                to_date = self.env.context.get("flexible_hours_to_date")
                employee = item.employee_ids[:1]
                if (from_date or to_date) and employee:
                    calendars = employee._get_planning_calendars(from_date, to_date)
                    hours = (
                        (
                            sum(
                                c.stored_full_time_required_hours
                                for c in calendars.calendar_id
                            )
                        )
                        if calendars
                        else False
                    )
            item.full_time_required_hours = hours

    @api.depends("hours_per_week", "company_id.resource_calendar_id.hours_per_week")
    def _compute_stored_full_time_required_hours(self):
        """This method is the same as _compute_full_time_required_hours()
        in the resource module.
        """
        for calendar in self.filtered("company_id"):
            calendar.stored_full_time_required_hours = (
                calendar.company_id.resource_calendar_id.hours_per_week
            )

    @api.depends(
        "attendance_ids",
        "attendance_ids.hour_from",
        "attendance_ids.hour_to",
        "two_weeks_calendar",
        "flexible_hours",
    )
    def _compute_stored_hours_per_day(self):
        """This method is the same as _compute_hours_per_day() in the resource
        module.
        """
        for calendar in self.filtered(lambda c: not c.flexible_hours):
            calendar.stored_hours_per_day = float_round(
                calendar._get_hours_per_day(), precision_digits=2
            )

    @api.depends(
        "auto_generate",
        "flexible_hours",
        "employee_ids.calendar_ids",
        "employee_ids.calendar_ids.calendar_id.stored_flexible_hours",
        "employee_ids.calendar_ids.calendar_id.stored_hours_per_day",
    )
    @api.depends_context(
        "flexible_hours_from_date",
        "flexible_hours_to_date",
    )
    def _compute_hours_per_day(self):
        """The value of hours_per_day is defined unless the calendar is auto_generate;
        in that case, the hours for the applicable calendars will be defined based
        on the dates specified by context.
        """
        res = super()._compute_hours_per_day()
        for item in self.filtered(lambda x: x.auto_generate and x.flexible_hours):
            from_date = self.env.context.get("flexible_hours_from_date")
            to_date = self.env.context.get("flexible_hours_to_date")
            employee = item.employee_ids[:1]
            hours = item.stored_hours_per_day
            if (from_date or to_date) and employee:
                calendars = employee._get_planning_calendars(from_date, to_date)
                hours = (
                    (sum(c.stored_hours_per_day for c in calendars.calendar_id))
                    if calendars
                    else False
                )
            item.hours_per_day = hours
        return res

    @api.constrains("active")
    def _check_active(self):
        for item in self:
            if not item.active:
                domain = [
                    ("calendar_id", "=", item.id),
                    "|",
                    ("date_end", "=", False),
                    ("date_end", ">=", fields.Date.context_today(self)),
                ]

                total_items = self.env["hr.employee.calendar"].search_count(domain)

                if total_items:
                    raise ValidationError(
                        self.env._(
                            "%(item_name)s is used in %(total_items)s employee(s). "
                            "You should change them first.",
                            item_name=item.name,
                            total_items=total_items,
                        )
                    )

    @api.constrains("company_id")
    def _check_company_id(self):
        for item in self.filtered("company_id"):
            total_items = self.env["hr.employee.calendar"].search_count(
                [
                    ("calendar_id", "=", item.id),
                    ("calendar_id.company_id", "=", item.company_id.id),
                    ("employee_id.company_id", "!=", item.company_id.id),
                    ("employee_id.company_id", "!=", False),
                ]
            )
            if total_items:
                raise ValidationError(
                    self.env._(
                        "%(item_name)s is used in %(total_items)s employee(s) "
                        "related to another company.",
                        item_name=item.name,
                        total_items=total_items,
                    )
                )

    def write(self, vals):
        res = super().write(vals)
        if "attendance_ids" in vals or "global_leave_ids" in vals:
            for record in self.filtered(lambda x: not x.auto_generate):
                calendars = self.env["hr.employee.calendar"].search(
                    [("calendar_id", "=", record.id)]
                )
                for employee in calendars.mapped("employee_id"):
                    employee._regenerate_calendar()
        return res

    def _attendance_intervals_batch(
        self, start_dt, end_dt, resources=None, domain=None, tz=None, lunch=False
    ):
        # It is important to define the appropriate context keys so that the value is
        # as expected.
        flexible_hours_from_date = start_dt.date()
        flexible_hours_to_date = end_dt.date()
        self = self.with_context(
            flexible_hours_from_date=flexible_hours_from_date,
            flexible_hours_to_date=flexible_hours_to_date,
        )
        resources = (
            resources.with_context(
                flexible_hours_from_date=flexible_hours_from_date,
                flexible_hours_to_date=flexible_hours_to_date,
            )
            if resources
            else None
        )
        return super()._attendance_intervals_batch(
            start_dt=start_dt,
            end_dt=end_dt,
            resources=resources,
            domain=domain,
            tz=tz,
            lunch=lunch,
        )

    def _get_unusual_days(self, start_dt, end_dt, company_id=False):
        # It is important to define the appropriate context keys so that the value is
        # as expected.
        self = self.with_context(
            flexible_hours_from_date=start_dt.date(),
            flexible_hours_to_date=end_dt.date(),
        )
        return super()._get_unusual_days(start_dt, end_dt, company_id)

    def _get_hours_for_date(self, target_date, day_period=None):
        # This method is used in hr.leave to get the start and end hours; if it is
        # auto-generated, we determine the appropriate resource.calendar to return
        # the "correct" hours (from that calendar).
        if self.auto_generate and self.employee_ids:
            employee = self.employee_ids[:1]
            calendars = employee._get_planning_calendars(target_date, target_date)
            if calendars:
                self = calendars[:1].calendar_id
        return super()._get_hours_for_date(target_date, day_period)
