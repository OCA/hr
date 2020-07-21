# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import api, fields, models


class HrEmployeeMedicalExamination(models.Model):

    _name = "hr.employee.medical.examination"
    _description = "Hr Employee Medical Examination"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, track_visibility="onchange",)

    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        readonly=True,
        track_visibility="onchange",
    )

    date = fields.Date(string="Examination Date", track_visibility="onchange",)
    result = fields.Selection(
        selection=[("failed", "Failed"), ("passed", "Passed")],
        track_visibility="onchange",
    )

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, track_visibility="onchange",
    )

    year = fields.Char("Year", default=lambda r: str(datetime.date.today().year))

    note = fields.Text(track_visibility="onchange")

    @api.onchange("date")
    def _onchange_date(self):
        for record in self:
            if record.date:
                record.year = str(record.date.year)

    def back_to_pending(self):
        self.write({"state": "pending"})

    def to_done(self):
        self.write({"state": "done"})

    def to_cancelled(self):
        self.write({"state": "cancelled"})

    def to_rejected(self):
        self.write({"state": "rejected"})
