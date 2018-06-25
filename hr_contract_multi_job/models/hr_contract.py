# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_job_ids = fields.One2many(
        'hr.contract.job',
        'contract_id',
        string='Jobs')

    # Modify the job_id field so that it points to the main job
    job_id = fields.Many2one(
        'hr.job',
        string="Job Title",
        compute="_compute_main_job_position",
        store=True)

    @api.depends('contract_job_ids')
    @api.multi
    def _compute_main_job_position(self):
        """
        Get the main job position from the field contract_job_ids which
        contains one and only one record with field is_main_job == True
        """
        for contract in self:
            main_job = contract.contract_job_ids.filtered('is_main_job').job_id
            contract.job_id = main_job

    @api.multi
    @api.constrains('contract_job_ids')
    def _check_one_main_job(self):
        for contract in self:
            # if the contract has no job assigned, a main job
            # is not required. Otherwise, one main job assigned is
            # required.
            if contract.contract_job_ids:
                main_jobs = contract.contract_job_ids.filtered('is_main_job')
                if len(main_jobs) != 1:
                    raise UserError(
                        _("You must assign one and only one job position "
                          "as main job position."))
