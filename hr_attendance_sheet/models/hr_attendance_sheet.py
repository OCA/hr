# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class HrAttendanceSheet(models.Model):
    _name = "hr.attendance.sheet"
    _description = "Attendance Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(compute="_compute_name", context_dependent=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    user_id = fields.Many2one(
        "res.users", related="employee_id.user_id", string="User", store=True
    )
    date_start = fields.Date(string="Date From", required=True, index=True)
    date_end = fields.Date(string="Date To", required=True, index=True)
    attendance_ids = fields.One2many(
        "hr.attendance", "attendance_sheet_id", string="Attendances"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Waiting Review"),
            ("done", "Approved"),
            ("locked", "Locked"),
        ],
        default="draft",
        track_visibility="onchange",
        string="Status",
        required=True,
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", related="employee_id.company_id"
    )
    department_id = fields.Many2one(
        "hr.department", string="Department", related="employee_id.department_id"
    )
    manager_id = fields.Many2one(
        "hr.employee", string="Manager", related="employee_id.parent_id"
    )
    working_hours = fields.Many2one(
        "resource.calendar",
        string="Working Hours",
        related="employee_id.resource_calendar_id",
    )
    hours_to_work = fields.Float(
        related="employee_id.hours_to_work",
        string="Hours to Work",
        help="""Expected working hours based on company policy. This is used \
             on attendance sheets to calculate overtime values.""",
    )
    total_time = fields.Float(compute="_compute_total_time", store=True)
    overtime = fields.Float(compute="_compute_overtime", store=True)
    can_review = fields.Boolean(
        string="Can Review", compute="_compute_can_review", search="_search_can_review"
    )
    reviewer_id = fields.Many2one(
        "hr.employee", string="Reviewer", readonly=True, track_visibility="onchange"
    )
    reviewed_on = fields.Datetime(string="Reviewed On", readonly=True)
    review_policy = fields.Selection(
        string="Review Policy", related="company_id.attendance_sheet_review_policy"
    )
    attendance_admin = fields.Many2one(
        "hr.employee",
        string="Attendance Admin",
        help="""In addition to the employees manager, this person can
        administer attendances for all employees in the department. This field
        is set on the department.""",
        related="department_id.attendance_admin",
    )

    # Automation Methods
    def activity_update(self):
        """Activity processing that shows in chatter for approval activity."""
        to_clean = self.env["hr.attendance.sheet"]
        to_do = self.env["hr.attendance.sheet"]
        for sheet in self:
            if sheet.state == "draft":
                to_clean |= sheet
            elif sheet.state == "confirm" and (
                sheet.review_policy == "employee_manager"
                or sheet.review_policy == "hr_or_manager"
            ):
                if sheet.sudo().employee_id.parent_id.user_id.id:
                    sheet.activity_schedule(
                        "hr_attendance_sheet." "mail_act_attendance_sheet_approval",
                        user_id=sheet.sudo().employee_id.parent_id.user_id.id,
                    )
            elif sheet.state == "done":
                to_do |= sheet
            elif sheet.state == "refuse":
                to_clean |= sheet
        if to_clean:
            to_clean.activity_unlink(
                ["hr_attendance_sheet.mail_act_attendance_sheet_approval"]
            )
        if to_do:
            to_do.activity_feedback(
                ["hr_attendance_sheet.mail_act_attendance_sheet_approval"]
            )

    # Scheduled Action Methods
    def _create_sheet_id(self):
        """Method used by the scheduling action to auto create sheets."""
        companies = (
            self.env["res.company"].search([("use_attendance_sheets", "=", True)]).ids
        )
        employees = self.env["hr.employee"].search(
            [
                ("use_attendance_sheets", "=", True),
                ("company_id", "in", companies),
                ("active", "=", True),
            ]
        )
        for employee in employees:
            if not employee.company_id.date_start or not employee.company_id.date_end:
                raise UserError(
                    _(
                        "Date From and Date To for Attendance \
                                   must be set on the Company %s"
                    )
                    % employee.company_id.name
                )
            sheet = self.env["hr.attendance.sheet"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("date_start", ">=", employee.company_id.date_start),
                    ("date_end", "<=", employee.company_id.date_end),
                ]
            )
            if not sheet:
                self.env["hr.attendance.sheet"].create(
                    {
                        "employee_id": employee.id,
                        "date_start": employee.company_id.date_start,
                        "date_end": employee.company_id.date_end,
                    }
                )
        self.check_pay_period_dates()

    def check_pay_period_dates(self):
        companies = self.env["res.company"].search(
            [("use_attendance_sheets", "!=", False)]
        )
        for company_id in companies:
            if datetime.today().date() > company_id.date_end:
                company_id.date_start = company_id.date_end + relativedelta(days=1)
                company_id.set_date_end(company_id.id)

    # Compute Methods
    @api.multi
    @api.depends("employee_id", "date_start", "date_end")
    def _compute_name(self):
        for sheet in self:
            if sheet.employee_id and sheet.date_start and sheet.date_end:
                sheet.name = (
                    sheet.employee_id.name
                    + " ("
                    + str(
                        datetime.strptime(
                            str(sheet.date_start), DEFAULT_SERVER_DATE_FORMAT
                        ).strftime("%m/%d/%y")
                    )
                    + " - "
                    + str(
                        datetime.strptime(
                            str(sheet.date_end), DEFAULT_SERVER_DATE_FORMAT
                        ).strftime("%m/%d/%y")
                    )
                    + ")"
                )

    @api.depends("attendance_ids.duration")
    def _compute_total_time(self):
        for sheet in self:
            sheet.total_time = sum(sheet.mapped("attendance_ids.duration"))

    @api.depends("total_time")
    def _compute_overtime(self):
        for sheet in self:
            overtime = sheet.total_time - sheet.hours_to_work
            if overtime < 0.0:
                sheet.overtime = 0.0
            else:
                sheet.overtime = overtime

    @api.depends("review_policy")
    def _compute_can_review(self):
        for sheet in self:
            sheet.can_review = self.env.user in sheet._get_possible_reviewers()

    # Reviewer Methods
    @api.multi
    def _get_possible_reviewers(self):
        res = self.env["res.users"].browse(SUPERUSER_ID)
        if self.review_policy == "hr":
            res |= self.env.ref("hr.group_hr_user").users
        elif self.review_policy == "employee_manager":
            if (
                self.department_id.attendance_admin
                and self.department_id.attendance_admin != self.employee_id
            ):
                res |= (
                    self.employee_id.parent_id.user_id
                    + self.department_id.attendance_admin.user_id
                )
            else:
                res |= self.employee_id.parent_id.user_id
        elif self.review_policy == "hr_or_manager":
            if (
                self.department_id.attendance_admin
                and self.department_id.attendance_admin != self.employee_id
            ):
                res |= (
                    self.employee_id.parent_id.user_id
                    + self.env.ref("hr.group_hr_user").users
                    + self.department_id.attendance_admin.user_id
                )
            else:
                res |= (
                    self.employee_id.parent_id.user_id
                    + self.env.ref("hr.group_hr_user").users
                )
        return res

    @api.multi
    def _check_can_review(self):
        if self.filtered(lambda x: not x.can_review and x.review_policy == "hr"):
            raise UserError(_("""Only a HR Officer can review the sheet."""))
        if self.filtered(
            lambda x: not x.can_review and x.review_policy == "employee_manager"
        ):
            raise UserError(
                _(
                    """Only the Manager of the Employee can review
            the sheet."""
                )
            )
        if self.filtered(
            lambda x: not x.can_review and x.review_policy == "hr_or_manager"
        ):
            raise UserError(
                _(
                    """Only the Manager of the Employee or an HR
            Officer/Manager can review the sheet."""
                )
            )

    # Create/Write Methods
    @api.model
    def create(self, vals):
        """On create, link existing attendances."""
        res = super(HrAttendanceSheet, self).create(vals)
        attendances = self.env["hr.attendance"].search(
            [
                ("employee_id", "=", res.employee_id.id),
                ("attendance_sheet_id", "=", False),
                ("check_in", ">=", res.date_start),
                ("check_in", "<=", res.date_end),
                "|",
                ("check_out", "=", False),
                "&",
                ("check_out", ">=", res.date_start),
                ("check_out", "<=", res.date_end),
            ]
        )
        attendances._compute_attendance_sheet_id()
        return res

    @api.multi
    def write(self, values):
        """Prevent writing on a locked sheet."""
        protected_fields = [
            "employee_id",
            "name",
            "attendance_ids",
            "date_start",
            "date_end",
        ]
        if self.state == "locked" and any(f in values.keys() for f in protected_fields):
            raise UserError(_("You can't edit a locked sheet."))
        elif (
            self.state in ("confirm", "done")
            and self.env.user not in self._get_possible_reviewers()
        ):
            raise UserError(
                _("You don't have permission to edit submitted/approved sheets")
            )
        return super(HrAttendanceSheet, self).write(values)

    # BUTTON ACTIONS
    @api.multi
    def attendance_action_change(self):
        """Call to perform Check In/Check Out action"""
        return self.employee_id.attendance_action_change()

    @api.multi
    def action_attendance_sheet_confirm(self):
        """Restrict to submit sheet contains attendance without checkout."""
        for sheet in self:
            ids_not_checkout = sheet.attendance_ids.filtered(
                lambda att: att.check_in and not att.check_out
            )
            if not ids_not_checkout:
                self.write({"state": "confirm"})
                self.activity_update()
            else:
                raise UserError(
                    _(
                        "The sheet cannot be validated as it does not "
                        + "contain an equal number of check-ins and check-outs."
                    )
                )

    @api.multi
    def action_attendance_sheet_draft(self):
        """Convert to Draft button."""
        if self.filtered(lambda sheet: sheet.state != "done"):
            raise UserError(_("Cannot revert to draft a non-approved sheet."))
        self._check_can_review()
        self.write({"state": "draft", "reviewer_id": False, "reviewed_on": False})
        self.activity_update()
        return True

    @api.multi
    def action_attendance_sheet_done(self):
        """Approve button."""
        if self.filtered(lambda sheet: sheet.state != "confirm"):
            raise UserError(_("Cannot approve a non-submitted sheet."))
        for sheet in self:
            ids_not_checkout = sheet.attendance_ids.filtered(
                lambda att: att.check_in and not att.check_out
            )
            if not ids_not_checkout:
                reviewer = self.env["hr.employee"].search(
                    [("user_id", "=", self.env.uid)], limit=1
                )
                if not reviewer:
                    raise UserError(
                        _(
                            """In order to review a attendance sheet,
                    your user needs to be linked to an employee record."""
                        )
                    )
                else:
                    self._check_can_review()
                    self.write(
                        {
                            "state": "done",
                            "reviewer_id": reviewer.id,
                            "reviewed_on": fields.Datetime.now(),
                        }
                    )
                    self.activity_update()
            else:
                raise UserError(
                    _(
                        "The sheet cannot be approved as it does "
                        + "not contain an equal number of sign ins and sign outs."
                    )
                )
        return True

    @api.multi
    def action_attendance_sheet_lock(self):
        """Lock button to lock the sheet and prevent any changes."""
        if self.filtered(lambda sheet: sheet.state != "done"):
            raise UserError(_("Cannot lock a non-approved sheet."))
        elif not self.env.user.has_group("hr_attendance.group_hr_attendance_user"):
            raise UserError(_("You do not have permissions to lock sheets."))
        else:
            self.write({"state": "locked"})
        return True

    @api.multi
    def action_attendance_sheet_unlock(self):
        """Unlock button, moves back to Confirm (Must have HR Group)."""
        if not self.env.user.has_group("hr_attendance.group_hr_attendance_user"):
            raise UserError(_("You do not have permissions to unlock sheets."))
        else:
            self.write({"state": "done"})
        return True

    @api.multi
    def action_attendance_sheet_refuse(self):
        """Refuse button sending back to draft."""
        if self.filtered(lambda sheet: sheet.state != "confirm"):
            raise UserError(_("Cannot reject a non-submitted sheet."))
        self._check_can_review()
        self.write({"state": "draft", "reviewer_id": False, "reviewed_on": False})
        self.activity_update()
        return True
