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
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.onchange('trial_date_start')
    @api.multi
    def onchange_trial_date_start(self):
        self.ensure_one()
        if self.trial_date_start:
            res = self.env.user.company_id.default_contract_trial_length
            if res:
                end_dt = fields.Date.from_string(
                    self.trial_date_start) + relativedelta(days=res)
                self.trial_date_end = fields.Date.to_string(end_dt)
