# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2016 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import operator
from openerp import models, fields, api


class hr_employee(models.Model):

    _inherit = 'hr.employee'

    contract_id = fields.Many2one(
        'hr.contract',
        'Current Contract',
        help='Latest contract of the employee',
        store=True,
        readonly=True,
        index=True,
        compute='_compute_current_contract'
    )
    first_contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        store=True,
        readonly=True,
        compute='_compute_first_contract'
    )
    job_id = fields.Many2one(
        'hr.job',
        'Job Title',
        readonly=True,
        store=True,
        related='contract_id.job_id'
    )

    @api.one
    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.employee_id',
        'contract_ids.job_id'
    )
    def _compute_first_contract(self):
        if len(self.contract_ids):
            contracts_sorted = self.contract_ids.sorted(
                key=operator.itemgetter('date_start', 'id'))
            self.first_contract_id = contracts_sorted[0]

    @api.one
    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.employee_id',
        'contract_ids.job_id'
    )
    def _compute_current_contract(self):
        if len(self.contract_ids):
            contracts_sorted = self.contract_ids.sorted(
                key=operator.itemgetter('date_start', 'id'))
            self.contract_id = contracts_sorted[-1]
