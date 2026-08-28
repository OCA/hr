# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2022-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command, Domain
from odoo.tools import config

SECTION_LINES = [
    Command.create(
        {
            "name": "Even week",
            "dayofweek": "0",
            "sequence": "0",
            "hour_from": 0,
            "day_period": "morning",
            "week_type": "0",
            "hour_to": 0,
            "display_type": "line_section",
        }
    ),
    Command.create(
        {
            "name": "Odd week",
            "dayofweek": "0",
            "sequence": "25",
            "hour_from": 0,
            "day_period": "morning",
            "week_type": "1",
            "hour_to": 0,
            "display_type": "line_section",
        }
    ),
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
        copy=True,
    )

    def _get_planning_calendars(self, from_date, to_date):
        self.ensure_one()
        # We need to use sudo to avoid the error  odoo.exceptions.AccessError:
        # The fields “calendar_ids”, which you are trying to read, are not
        # available for employee public profiles.
        return self.sudo().calendar_ids.filtered(
            lambda x: (not x.date_start or (from_date and x.date_start <= from_date))
            and (not x.date_end or (to_date and x.date_end >= to_date))
        )

    @api.model
    def default_get(self, fields):
        """Set calendar_ids default value to cover all use cases."""
        vals = super().default_get(fields)
        if "calendar_ids" in fields and not vals.get("calendar_ids"):
            vals["calendar_ids"] = [
                Command.create(
                    {"calendar_id": self.env.company.resource_calendar_id.id}
                ),
            ]
        return vals

    def _regenerate_calendar(self):
        self.ensure_one()
        vals_list = []
        today = fields.Date.context_today(self)
        active_planning = self._get_planning_calendars(today, today)
        if active_planning:
            planning_to_use = active_planning[:1]
        elif self.calendar_ids:
            sorted_calendars = self.calendar_ids.sorted(
                key=lambda r: r.date_end or r.date_start, reverse=True
            )
            planning_to_use = sorted_calendars[:1]
        else:
            return
        current_calendar = planning_to_use.calendar_id
        two_weeks = bool(current_calendar.two_weeks_calendar)
        if self.resource_id.calendar_id.auto_generate:
            self.resource_calendar_id.attendance_ids.unlink()
            self.resource_calendar_id.two_weeks_calendar = two_weeks
        seq = 0
        for week in ["0", "1"] if two_weeks else ["0"]:
            if two_weeks:
                section_vals = SECTION_LINES[int(week)]
                section_vals[2]["sequence"] = seq
                vals_list.append(section_vals)
                seq += 1
            if two_weeks:
                attendances = current_calendar.attendance_ids.filtered(
                    lambda x, w=week: x.week_type == w
                )
            else:
                attendances = current_calendar.attendance_ids
            for attendance_line in attendances:
                if attendance_line.display_type == "line_section":
                    continue
                data = attendance_line.copy_data(
                    {
                        "calendar_id": self.resource_calendar_id.id,
                        "week_type": week if two_weeks else False,
                        "sequence": seq,
                    }
                )[0]
                seq += 1
                vals_list.append((0, 0, data))
        if not self.resource_id.calendar_id.auto_generate:
            self.resource_id.calendar_id = (
                self.env["resource.calendar"]
                .create(
                    {
                        "active": False,
                        "company_id": self.company_id.id,
                        "auto_generate": True,
                        "name": self.env._("Auto generated calendar for employee")
                        + f" {self.name}",
                        "attendance_ids": vals_list,
                        "two_weeks_calendar": two_weeks,
                        "tz": self.tz,
                    }
                )
                .id
            )
        else:
            self.resource_calendar_id.attendance_ids = vals_list
        if planning_to_use:
            self.resource_id.calendar_id.hours_per_day = current_calendar.hours_per_day
            self.copy_global_leaves()

    def _get_work_days_data_batch(
        self,
        from_datetime,
        to_datetime,
        compute_leaves=True,
        calendar=None,
        domain=None,
    ):
        # Override function that change the calendar depending on date
        if len(self) == 1 and self.calendar_ids:
            from_dt_tz = fields.Datetime.context_timestamp(self, from_datetime)
            check_date = from_dt_tz.date()
            planned_line = self._get_planning_calendars(check_date, check_date)
            if planned_line:
                best_line = sorted(
                    planned_line,
                    key=lambda c: (c.date_end - c.date_start).days
                    if c.date_start and c.date_end
                    else 9999,
                )[0]
                calendar = best_line.calendar_id
        res = super()._get_work_days_data_batch(
            from_datetime,
            to_datetime,
            compute_leaves=compute_leaves,
            calendar=calendar,
            domain=domain,
        )
        return res

    def copy_global_leaves(self):
        self.ensure_one()
        leave_ids = []
        today = fields.Date.context_today(self)
        active_planning = self._get_planning_calendars(today, today)
        if not active_planning and self.calendar_ids:
            active_planning = self.calendar_ids.sorted(
                key=lambda r: r.date_end or r.date_start, reverse=True
            )[:1]

        for calendar in active_planning:
            global_leaves = calendar.calendar_id.global_leave_ids
            if calendar.date_start:
                global_leaves = global_leaves.filtered(
                    lambda x, c=calendar: x.date_from.date() >= c.date_start
                )
            if calendar.date_end:
                global_leaves = global_leaves.filtered(
                    lambda x, c=calendar: x.date_from.date() <= c.date_end
                )
            leave_ids += global_leaves.ids
        vals = [
            leave.copy_data({"calendar_id": self.resource_id.calendar_id.id})[0]
            for leave in self.env["resource.calendar.leaves"].search(
                [("id", "in", leave_ids)], order="date_from asc"
            )
        ]
        existing_leaves_mapping = {
            e.date_from: e for e in self.resource_id.calendar_id.global_leave_ids
        }
        requested_create_dates = [(e.get("date_from"), e.get("date_to")) for e in vals]
        new_vals = [
            v
            for v in vals
            if not (
                v.get("date_from") in existing_leaves_mapping
                and v.get("date_to")
                == existing_leaves_mapping[v.get("date_from")].date_to
            )
        ]
        to_unlink = self.resource_id.calendar_id.global_leave_ids.filtered(
            lambda x: (x.date_from, x.date_to) not in requested_create_dates
        )
        to_unlink.unlink()
        return self.env["resource.calendar.leaves"].create(new_vals).ids

    def regenerate_calendar(self):
        for item in self:
            item._regenerate_calendar()

    def copy(self, default=None):
        self.ensure_one()
        new = super().copy(default)
        # Define a good main calendar for being able to regenerate it later
        new.resource_id.calendar_id = fields.first(new.calendar_ids).calendar_id
        new.filtered("calendar_ids").regenerate_calendar()
        return new

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # Avoid creating an employee without calendars
        if (
            not self.env.context.get("skip_employee_calendars_required")
            and not config["test_enable"]
            and not self.env.context.get("install_mode")
            and res.filtered(lambda x: not x.calendar_ids)
        ):
            raise UserError(
                self.env._("You can not create employees without any calendar.")
            )
        for employee in res.filtered("calendar_ids"):
            employee.sudo().regenerate_calendar()
        return res


class HrEmployeeCalendar(models.Model):
    _name = "hr.employee.calendar"
    _description = "Employee Calendar"
    _order = "date_end desc"

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="employee_id.company_id")
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
        check_company=True,
        ondelete="restrict",
    )

    _date_consistency = models.Constraint(
        "CHECK(date_start <= date_end)",
        "Date end should be higher than date start",
    )

    def _related_action_format_error_message(self):
        return self.env._(
            "The employee %s has already a calendar assigned that overalps this period",
            self.employee_id.name,
        )

    @api.constrains("date_start", "date_end", "employee_id")
    def _check_overlap(self):
        for record in self:
            domain = Domain(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if record.date_end:
                domain &= Domain(
                    [
                        "|",
                        ("date_start", "<=", record.date_end),
                        ("date_start", "=", False),
                    ]
                )
            if record.date_start:
                domain &= Domain(
                    [
                        "|",
                        ("date_end", ">=", record.date_start),
                        ("date_end", "=", False),
                    ]
                )
            if self.search_count(list(domain)):
                raise UserError(record._related_action_format_error_message())

    @api.model_create_multi
    def create(self, vals):
        calendars = super().create(vals)
        for calendar in calendars:
            calendar.employee_id.sudo()._regenerate_calendar()
        return calendars

    def write(self, vals):
        res = super().write(vals)
        for employee in self.mapped("employee_id"):
            employee._regenerate_calendar()
        return res

    def unlink(self):
        employees = self.mapped("employee_id")
        res = super().unlink()
        for employee in employees:
            employee._regenerate_calendar()
        return res
