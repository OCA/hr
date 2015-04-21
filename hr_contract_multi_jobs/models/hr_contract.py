# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    @api.depends('contract_job_ids', 'contract_job_ids.contract_id')
    def _get_main_job_position(self):
        """
        Get the main job position from the field contract_job_ids which
        contains one and only one record with field is_main_job == True
        """
        for contract in self:
            job_id = False
            for contract_job in contract.contract_job_ids:
                if contract_job.is_main_job:
                    job_id = contract_job.job_id.id
                    break
            contract.job_id = job_id

    contract_job_ids = fields.One2many('hr.contract.job',
                                       'contract_id',
                                       string='Jobs')

    # Modify the job_id field so that it points to the main job
    job_id = fields.Many2one(
        'hr.job',
        string="Job Title",
        compute="_get_main_job_position",
        store=True)

    @api.model
    @api.depends('contract_job_ids', 'contract_job_ids.is_main_job')
    @api.constrains('contract_job_ids')
    def _check_one_main_job(self):
        for contract in self:

            # if the contract has no job assigned, a main job
            # is not required. Otherwise, one main job assigned is
            # required.
            if contract.contract_job_ids:
                main_jobs = [
                    contract_job
                    for contract_job in contract.contract_job_ids
                    if contract_job.is_main_job
                ]
                if len(main_jobs) != 1:
                    raise exceptions.Warning(
                        _("You must assign one and only one job position "
                          "as main job position."))
