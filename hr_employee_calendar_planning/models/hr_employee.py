# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

SECTION_LINES = [
    (
        0,
        0,
        {
            "name": "Even week",
            "dayofweek": "0",
            "sequence": "0",
            "hour_from": 0,
            "day_period": "morning",
            "week_type": "0",
            "hour_to": 0,
            "display_type": "line_section",
        },
    ),
    (
        0,
        0,
        {
            "name": "Odd week",
            "dayofweek": "0",
            "sequence": "25",
            "hour_from": 0,
            "day_period": "morning",
            "week_type": "1",
            "hour_to": 0,
            "display_type": "line_section",
        },
    ),
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
    )

    def _regenerate_calendar(self):
        self.ensure_one()
        vals_list = []
        two_weeks = bool(
            self.calendar_ids.mapped("calendar_id").filtered("two_weeks_calendar")
        )
        if (
            not self.resource_id.calendar_id
            or not self.resource_id.calendar_id.auto_generate
        ):
            self.resource_calendar_id = (
                self.env["resource.calendar"]
                .create(
                    {
                        "active": False,
                        "auto_generate": True,
                        "name": _("Auto generated calendar for employee")
                        + " %s" % self.name,
                        "attendance_ids": [],
                        "two_weeks_calendar": two_weeks,
                    }
                )
                .id
            )
        else:
            self.resource_calendar_id.attendance_ids.unlink()
            self.resource_calendar_id.two_weeks_calendar = two_weeks
        seq = 0
        for line in self.calendar_ids:
            for attendance_line in line.calendar_id.attendance_ids:
                if attendance_line.display_type == "line_section":
                    continue
                duplicate = two_weeks and not line.calendar_id.two_weeks_calendar
                week_odd = attendance_line.week_type == "1"
                data = attendance_line.copy_data(
                    {
                        "calendar_id": self.resource_calendar_id.id,
                        "date_from": line.date_start,
                        "date_to": line.date_end,
                        "week_type": "0" if duplicate else attendance_line.week_type,
                        "sequence": seq + 26 if week_odd else 24 - seq,
                        # To make sure sequence of odd weeks is greater than 25
                        # and sequence of even weeks is less than 25, as in
                        # /resource/models/resource.py#L266
                    }
                )[0]
                seq += 1
                vals_list.append((0, 0, data))
                if duplicate:
                    data = attendance_line.copy_data(
                        {
                            "calendar_id": self.resource_calendar_id.id,
                            "date_from": line.date_start,
                            "date_to": line.date_end,
                            "week_type": "1",
                            "sequence": seq + 26,
                        },
                    )[0]
                    seq += 1
                    vals_list += [(0, 0, data)]
        if two_weeks:
            SECTION_LINES[0][2]["sequence"] = -seq
            vals_list = SECTION_LINES + vals_list
        self.resource_calendar_id.attendance_ids = vals_list

    def regenerate_calendar(self):
        self._regenerate_calendar()


class HrEmployeeCalendar(models.Model):
    _name = "hr.employee.calendar"
    _description = "Employee Calendar"
    _order = "date_end desc"

    date_start = fields.Date(
        string="Start Date",
    )
    date_end = fields.Date(
        string="End Date",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
    )
    company_id = fields.Many2one(related="employee_id.company_id")
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
        check_company=True,
    )

    _sql_constraints = [
        (
            "date_consistency",
            "CHECK(date_start <= date_end)",
            "Date end should be higher than date start",
        ),
    ]

    @api.model_create_multi
    def create(self, vals):
        record = super(HrEmployeeCalendar, self).create(vals)
        record.employee_id._regenerate_calendar()
        return record

    def write(self, vals):
        res = super(HrEmployeeCalendar, self).write(vals)
        for employee in self.mapped("employee_id"):
            employee._regenerate_calendar()
        return res

    def unlink(self):
        employees = self.mapped("employee_id")
        res = super(HrEmployeeCalendar, self).unlink()
        for employee in employees:
            employee._regenerate_calendar()
        return res
