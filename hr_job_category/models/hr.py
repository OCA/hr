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

    def _remove_tags(self, job_id):
        if isinstance(job_id, int):
            job = self.env["hr.job"].browse(job_id)
        else:
            job = job_id
        for employee in self.mapped("employee_id"):
            _logger.debug(
                "Removing employee tags if tags exist on contract job: %s",
                employee.category_ids,
            )
            tags_to_remove = [
                (3, tag.id) for tag in job.category_ids & employee.category_ids
            ]
            if tags_to_remove:
                employee.write({"category_ids": tags_to_remove})

    def _tag_employees(self, job_id):
        if isinstance(job_id, int):
            job = self.env["hr.job"].browse(job_id)
        else:
            job = job_id
        _logger.debug(
            "Adding employee tags if job tags doesn't exist: %s", job.category_ids
        )
        for employee in self.mapped("employee_id"):
            tags_to_add = [
                (4, tag.id) for tag in job.category_ids - employee.category_ids
            ]
            if tags_to_add:
                employee.write({"category_ids": tags_to_add})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "job_id" in vals:
            res._tag_employees(vals.get("job_id"))
        return res

    def write(self, vals):
        prev_data = {
            res["id"]: res["job_id"][0]
            for res in self.read(["job_id"])
            if res["job_id"]
        }
        for record in self:
            if (
                "employee_id" in vals
                and record.employee_id
                and record.employee_id.id != vals.get("employee_id")
            ):
                record._remove_tags(record.job_id)
        res = super().write(vals)
        # Go through each record and delete tags associated with the previous
        # job, then add the tags of the new job.
        #
        if "job_id" in vals:
            for contract in self:
                job_id = prev_data.get(contract.id)
                if job_id:
                    contract._remove_tags(job_id)
                self._tag_employees(contract.job_id)
        return res

    def unlink(self):
        # Go through each record and delete tags associated with the previous job
        for contract in self:
            if contract.job_id:
                contract._remove_tags(contract.job_id)
        return super().unlink()
