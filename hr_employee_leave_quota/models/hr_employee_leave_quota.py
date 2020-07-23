# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    leave_type_ids = fields.One2many(
        string="Holiday Quota",
        comodel_name="hr.employee.leave.quota",
        inverse_name="employee_id",
    )


class HrEmployeeLeaveQuota(models.Model):
    _name = "hr.employee.leave.quota"

    employee_id = fields.Many2one(
        string="Employee", comodel_name="hr.employee", readonly=True,
    )
    leave_type = fields.Selection(
        [("sick", "Sick"), ("vacation", "Vacation")],
        string="Leave Type",
        required=True,
    )
    quota = fields.Integer(string="Quota",)
    used_days = fields.Integer(string="Used (days)",)
    balance = fields.Integer(string="Balance", compute="_compute_balance",)

    @api.depends("quota", "used_days")
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.quota - rec.used_days


class HrEmployeeLeaveRequest(models.Model):
    _name = "hr.employee.leave.request"

    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        default=lambda self: self._default_hr_employee(),
        readonly=True,
    )
    approver_id = fields.Many2one("res.users", string="Approve By", readonly=True,)
    request_line_ids = fields.One2many(
        "hr.employee.leave.request.line", inverse_name="request_id",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting", "Waiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        track_visibility="onchange",
    )

    def _default_hr_employee(self):
        Employee = self.env["hr.employee"]
        employee = Employee.search([("user_id", "=", self.env.user.id)])
        return employee.id

    def button_draft(self):
        self.write({"state": "draft"})

    def button_submit_approved(self):
        self.write({"state": "waiting"})

    def button_approve(self):
        for rec in self:
            Employee = rec.employee_id
            Quota = Employee.leave_type_ids
            Resuest_line = rec.request_line_ids
            for r in Resuest_line:
                leave_type = Quota.filtered(
                    lambda self: self.leave_type == r.leave_type
                )
                leave_type.used_days = leave_type.used_days + r.leave_days
                leave_type.balance = leave_type.quota - leave_type.used_days
        self.write({"state": "approved", "approver_id": self.env.user.id})

    def button_rejected(self):
        self.write({"state": "rejected"})


class HrEmployeeLeaveRequestLine(models.Model):
    _name = "hr.employee.leave.request.line"

    request_id = fields.Many2one("hr.employee.leave.request",)
    leave_type = fields.Selection(
        [("sick", "Sick"), ("vacation", "Vacation")],
        string="Leave Type",
        required=True,
    )
    date_start = fields.Date(string="Date Start",)
    date_end = fields.Date(string="Date End",)
    leave_days = fields.Float(
        string="Leave Days",
        compute="_compute_leave_days",
        inverse="_inverse_leave_days",
    )
    balance = fields.Integer(string="Balance", compute="_compute_balance")

    @api.depends("date_start", "date_end")
    def _compute_leave_days(self):
        for r in self:
            if r.date_start and r.date_end:
                r.leave_days = (r.date_end - r.date_start).days + 1
            else:
                r.leave_days = 0.0

    def _inverse_leave_days(self):
        for r in self:
            if not (r.date_start and r.leave_days):
                r.date_end = r.date_start
            else:
                leave_days = timedelta(days=r.leave_days, seconds=-1)
                r.date_end = r.date_start + leave_days

    @api.constrains("balance")
    def _check_balance(self):
        for r in self:
            if r.balance < 0:
                raise ValidationError(_("Balance < 0"))

    @api.constrains("date_start", "date_end")
    def _check_start_end_date(self):
        for r in self:
            if r.date_start > r.date_end:
                raise ValidationError(_("Date Start > Date End"))

    @api.depends("leave_days")
    def _compute_balance(self):
        for rec in self:
            Request = rec.request_id
            Employee = Request.employee_id
            Quota = Employee.leave_type_ids
            leave_type = Quota.filtered(lambda self: self.leave_type == rec.leave_type)
            rec.balance = leave_type.balance - rec.leave_days
