# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
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
import math

from openerp import models, api, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    terminal_benefit = fields.Float(
        'End of Service Benefit',
        readonly=True,
        compute='_compute_terminal_benefit'
    )

    @api.one
    @api.depends('date_start', 'contract_ids', 'contract_ids.wage')
    def _compute_terminal_benefit(self):
        res = 0
        if not self.contract_id or not self.length_of_service:
            self.terminal_benefit = res
            return
        service_length = self.length_of_service
        rules = self.contract_id.type_id.terminal_rule_ids.filtered(
            lambda r: (r.range_from <= service_length
                       and r.range_to > service_length)
        )
        if rules:
            res = (self.contract_id.wage * rules.days
                   * math.ceil(service_length))
        self.terminal_benefit = res
