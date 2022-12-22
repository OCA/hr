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

    def _remove_tags(self, employee_id=None, job_id=None):
        # TODO write tags only once
        if not employee_id or not job_id:
            return
        employee = self.env["hr.employee"].browse(employee_id)
        empl_tags = employee.category_ids
        job = self.env["hr.job"].browse(job_id)
        _logger.debug(
            "Removing employee tags if tag exists on contract " "job: %s", empl_tags
        )
        for tag in job.category_ids:
            if tag in empl_tags:
                employee.write({"category_ids": [(3, tag.id)]})

    def _tag_employees(self, employee_id=None, job_id=None):
        if not employee_id or not job_id:
            return
        employee = self.env["hr.employee"].browse(employee_id)
        empl_tags = employee.category_ids
        job = self.env["hr.job"].browse(job_id)
        for tag in job.category_ids:
            if tag not in empl_tags:
                _logger.debug(
                    "Adding employee tag if job tag doesn't " "exists: %s", tag.name
                )
                employee.write({"category_ids": [(4, tag.id)]})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "job_id" in vals:
            res._tag_employees(vals.get("job_id"))
        return res

    def write(self, vals):
        prev_data = self.read(["job_id"])
        if "employee_id" in vals and self.employee_id != vals.get("employee_id"):
            self._remove_tags(self.employee_id.id, self.job_id.id)
        res = super().write(vals)
        # Go through each record and delete tags associated with the previous
        # job, then add the tags of the new job.
        #

        for contract in self:
            for data in prev_data:
                if (
                    data.get("id") == contract.id
                    and data["job_id"]
                    and data["job_id"][0] != contract.job_id.id
                ):
                    self._remove_tags(contract.employee_id.id, data["job_id"][0])
                self._tag_employees(contract.employee_id.id, contract.job_id.id)
        return res

    def unlink(self):
        prev_data = self.read(["job_id"])
        # Go through each record and delete tags associated with the previous
        # job, then add the tags of the new job.
        #
        for contract in self:
            for data in prev_data:
                self._remove_tags(contract.employee_id.id, data["job_id"][0])
        return super(HRContract, self).unlink()
