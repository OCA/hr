# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class hr_job(models.Model):
    _inherit = 'hr.job'

    category_ids = fields.Many2many('hr.employee.category',
                                    'job_category_rel',
                                    'job_id',
                                    'category_id',
                                    string='Associated Tags')


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    @api.one
    def _remove_tags(self, employee_id=None, job_id=None):
        if not employee_id or not job_id:
            return
        employee = self.env['hr.employee'].browse(employee_id)
        empl_tags = employee.category_ids
        job = self.env['hr.job'].browse(job_id)
        _logger.debug('Removing employee tags if tag exists on contract '
                      'job: %s', empl_tags)
        for tag in job.category_ids:
            if tag in empl_tags:
                employee.write({'category_ids': [(3, tag.id)]})

    @api.one
    def _tag_employees(self, employee_id=None, job_id=None):
        if not employee_id or not job_id:
            return
        employee = self.env['hr.employee'].browse(employee_id)
        empl_tags = employee.category_ids
        job = self.env['hr.job'].browse(job_id)
        for tag in job.category_ids:
            if tag not in empl_tags:
                _logger.debug("Adding employee tag if job tag doesn't "
                              "exists: %s", tag.name)
                employee.write({'category_ids': [(4, tag.id)]})

    @api.model
    def create(self, vals):
        res = super(hr_contract, self).create(vals)
        self._tag_employees(vals.get('employee_id', False),
                            vals.get('job_id', False))
        return res

    @api.multi
    def write(self, vals):
        prev_data = self.read(['job_id'])

        res = super(hr_contract, self).write(vals)

        # Go through each record and delete tags associated with the previous
        # job, then add the tags of the new job.
        #
        for contract in self:
            for data in prev_data:
                if (data.get('id') == contract.id and data['job_id'] and
                        data['job_id'][0] != contract.job_id.id):
                    self._remove_tags(contract.employee_id.id,
                                      data['job_id'][0])
                self._tag_employees(contract.employee_id.id,
                                    contract.job_id.id)
        return res
