# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('contract_ids')
    def _get_latest_contract(self):
        res = {}
        obj_contract = self.env['hr.contract']
        for emp in self:
            last_contract = False
            contract_ids = emp.contract_ids.sorted(key=lambda r: r.date_start)
            if contract_ids:
                last_contract = contract_ids[-1:][0]
            emp.contract_id = last_contract and last_contract.id or False

    @api.multi
    def _get_id_from_contract(self):
        res = []
        for contract in self.env['hr.contract'].browse([]):
            res.append(contract.employee_id.id)
        return res

    contract_id = fields.Many2one("hr.contract", string="Contract",
                                  compute="_get_latest_contract",
                                  store=True,
                                  help="Latest contract of the employee"),
    job_id = fields.Many2one("hr.job", string="Job",
                             related="contract_id.job_id")

    _sql_constraints = [
        ('unique_identification_id', 'unique(identification_id)',
         _('Official Identifications must be unique!')),
    ]
