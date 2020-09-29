# Copyright 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HRJob(models.Model):
    _inherit = "hr.job"

    category_ids = fields.Many2many(
        "hr.employee.category",
        "job_category_rel",
        "job_id",
        "category_id",
        string="Associated Tags",
    )


class HRContract(models.Model):
    _inherit = "hr.contract"

    def _tag_employees(self, job_id):
        if job_id:
            job = self.env["hr.job"].browse(job_id)
            self.mapped("employee_id").write(
                {"category_ids": [(6, 0, job.category_ids.ids)]}
            )
        else:
            for contract in self:
                categories = contract.job_id and contract.job_id.category_ids.ids or []
                contract.employee_id.write({"category_ids": [(6, 0, categories)]})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "job_id" in vals:
            res._tag_employees(vals.get("job_id"))
        return res

    def write(self, vals):
        if "employee_id" in vals:
            self.mapped("employee_id").write({"category_ids": [(5,)]})
        res = super().write(vals)
        if "job_id" in vals or ("employee_id" in vals and vals["employee_id"]):
            self._tag_employees(vals.get("job_id"))
        return res

    def unlink(self):
        self.mapped("employee_id").write({"category_ids": [(5,)]})
        return super().unlink()
