# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

import pytz
from datetime import datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_sheet_id = fields.Many2one(
        "hr.attendance.sheet",
        string="Sheet",
        compute="_compute_attendance_sheet_id",
        store=True,
    )
    duration = fields.Float(
        string="Duration (Hrs)",
        compute="_compute_duration",
    )
    auto_lunch = fields.Boolean(
        string="Auto Lunch Applied",
        help="If Auto Lunch is enabled and applied on this attendance.",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", related="attendance_sheet_id.company_id"
    )
    auto_lunch_enabled = fields.Boolean(
        string="Auto Lunch Enabled", related="company_id.auto_lunch"
    )
    override_auto_lunch = fields.Boolean(
        string="Override Auto Lunch",
        help="Enable if you don't want the auto lunch to calculate.",
    )
    override_reason = fields.Text(
        string="Override Reason",
        help="State the reason you are overriding the auto lunch.",
    )
    attendance_admin = fields.Many2one(
        "hr.employee",
        string="Attendance Admin",
        help="""In addition to the employees manager, this person can
        administer attendances for all employees in the department. This field
        is set on the department.""",
        related="department_id.attendance_admin",
    )

    # Get Methods
    def _get_attendance_employee_tz(self, date=None):
        """Convert date according to timezone of user"""
        tz = False
        if self.employee_id:
            tz = self.employee_id.tz
        if not date:
            return False
        time_zone = pytz.timezone(tz or "UTC")
        attendance_dt = datetime.strptime(str(date), DEFAULT_SERVER_DATETIME_FORMAT)
        attendance_tz_dt = pytz.UTC.localize(attendance_dt)
        attendance_tz_dt = attendance_tz_dt.astimezone(time_zone)
        attendance_tz_date_str = datetime.strftime(
            attendance_tz_dt, DEFAULT_SERVER_DATE_FORMAT
        )
        return attendance_tz_date_str

    def _get_attendance_state(self):
        """Check and raise error if related sheet is not in 'draft' state"""
        if self.attendance_sheet_id and self.attendance_sheet_id.state == "locked":
            raise UserError(_("You cannot modify an entry in a locked sheet."))
        elif (
            self.attendance_sheet_id.state == "done"
            and self.env.user not in self.attendance_sheet_id._get_possible_reviewers()
        ):
            raise UserError(_("You cannot modify an entry in a approved sheet"))
        return True

    # Compute Methods
    @api.depends("employee_id", "check_in", "check_out")
    def _compute_attendance_sheet_id(self):
        """Find and set current sheet in current attendance record"""
        for attendance in self:
            sheet_obj = self.env["hr.attendance.sheet"]
            check_in = False
            if attendance.check_in:
                check_in = attendance._get_attendance_employee_tz(
                    date=attendance.check_in
                )
                domain = [("employee_id", "=", attendance.employee_id.id)]
                if check_in:
                    domain += [
                        ("date_start", "<=", check_in),
                        ("date_end", ">=", check_in),
                    ]
                    attendance_sheet_ids = sheet_obj.search(domain, limit=1)
                    if attendance_sheet_ids.state not in ("locked", "done"):
                        attendance.attendance_sheet_id = attendance_sheet_ids or False

    @api.multi
    def _compute_duration(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                delta = rec.check_out - rec.check_in
                rec.duration = delta.total_seconds() / 3600

                # If auto lunch is enabled for the company and time between
                # other attendances < lunch period, then adjust the duration
                # calculation for the first attendance.
                if (
                    rec.company_id.auto_lunch
                    and rec.duration > rec.company_id.auto_lunch_duration != 0.0
                    and not rec.override_auto_lunch
                ):
                    day_start = rec.check_in.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    day_end = rec.check_out.replace(
                        hour=23, minute=59, second=59, microsecond=59
                    )
                    first_attendance = self.env["hr.attendance"].search(
                        [
                            ("check_in", ">=", day_start),
                            ("check_in", "<=", day_end),
                            ("employee_id", "=", rec.employee_id.id),
                        ],
                        order="check_in asc",
                        limit=1,
                    )
                    today_attendances = self.env["hr.attendance"].search(
                        [
                            ("check_in", ">=", day_start),
                            ("check_in", "<=", day_end),
                            ("employee_id", "=", rec.employee_id.id),
                        ]
                    )
                    time_between_attendances = 0.0
                    if first_attendance and first_attendance.id == rec.id:
                        if len(today_attendances) > 1:
                            for attendance in today_attendances:
                                if attendance.id != first_attendance.id:
                                    delta2 = (
                                        attendance.check_in - first_attendance.check_out
                                    )
                                    time_between_attendances = (
                                        delta2.total_seconds() / 3600
                                    )
                                    rec.write({"auto_lunch": False})
                            if (
                                time_between_attendances
                                < rec.company_id.auto_lunch_hours
                            ):
                                rec.duration = (
                                    delta.total_seconds() / 3600
                                ) - rec.company_id.auto_lunch_hours
                                rec.write({"auto_lunch": True})
                        else:
                            rec.duration = (
                                delta.total_seconds() / 3600
                            ) - rec.company_id.auto_lunch_hours
                            rec.write({"auto_lunch": True})
                    else:
                        rec.write({"auto_lunch": False})
                elif rec.company_id.auto_lunch and rec.auto_lunch:
                    rec.write({"auto_lunch": False})

    # Unlink/Write/Create Methods
    @api.multi
    def unlink(self):
        """Restrict to delete attendance from confirmed/locked sheet"""
        for attendance in self:
            attendance._get_attendance_state()
        return super(HrAttendance, self).unlink()

    @api.multi
    def write(self, vals):
        """Restrict to write attendance from confirmed/locked sheet."""
        protected_fields = ["employee_id", "check_in", "check_out"]
        for attendance in self:
            if attendance.attendance_sheet_id.state in ("locked", "done") and any(
                f in vals.keys() for f in protected_fields
            ):
                attendance._get_attendance_state()
        return super(HrAttendance, self).write(vals)
