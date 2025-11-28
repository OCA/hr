# Copyright 2025 PT Solusi Aglis Indonesia. (https://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class HRJob(models.Model):
    _inherit = "hr.job"

    employee_count = fields.Integer(compute="_compute_employee_count")

    def action_open_employees(self):
        self.ensure_one()
        if self.env["hr.employee"].has_access("read"):
            res_model = "hr.employee"
        else:
            res_model = "hr.employee.public"

        return {
            "name": _("Related Employees"),
            "type": "ir.actions.act_window",
            "res_model": res_model,
            "view_mode": "list,kanban,form",
            "views": [(False, "list"), (False, "kanban"), (False, "form")],
            "context": {
                "default_job_id": self.id,
                "search_default_group_job": 1,
                "search_default_job_id": self.id,
                "expand": 1,
            },
        }

    def _compute_employee_count(self):
        res = {
            job.id: count
            for job, count in self.env["hr.employee"]
            .sudo()
            ._read_group(
                domain=[
                    ("job_id", "in", self.ids),
                ],
                groupby=["job_id"],
                aggregates=["__count"],
            )
        }

        for job in self:
            job.employee_count = res.get(job.id, 0)
