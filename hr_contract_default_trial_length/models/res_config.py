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
from openerp import fields, models, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.config.settings'

    default_contract_trial_length = fields.Integer(
        default=60,
        help="Default contract trial length in Days"
    )

    @api.model
    def get_default_contract_trial_length(self, fields):
        company = self.env.user.company_id
        return {
            'default_contract_trial_length': (
                company.default_contract_trial_length)
        }

    @api.one
    def set_struct_id(self):
        company = self.env.user.company_id
        company.default_contract_trial_length = (
            self.default_contract_trial_length)
