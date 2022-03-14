# Copyright 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContractJob(models.Model):
    """
    An instance of a job position for an employee's contract.

    This model may look trivial for now, but the purpose is that other modules
    add fields to it, e.g. a salary class or a wage scale. These are fields
    that depend on both the contract and the job position.
    """

    _name = "hr.contract.job"
    _description = "Relational object between contract and job"

    name = fields.Char(string="Job Name", related="job_id.name", index=True)
    job_id = fields.Many2one("hr.job", required=True, ondelete="cascade")
    contract_id = fields.Many2one("hr.contract", required=True, ondelete="cascade")
    is_main_job = fields.Boolean(string="Main Job Position")
