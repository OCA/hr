# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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


class hr_contract_job(models.Model):
    _inherit = 'hr.contract.job'

    @api.multi
    def _get_current_hourly_rate(self):
        today = fields.Date.today()
        for contract_job in self:
            contract = contract_job.contract_id
            if contract_job.hourly_rate_class_id and \
                    contract.salary_computation_method == 'hourly_rate':
                rate_class = contract_job.hourly_rate_class_id
                rates = [
                    r for r in rate_class.line_ids
                    if(r.date_start <= today and (not r.date_end or
                                                  today <= r.date_end))]
                contract_job.hourly_rate = rates and rates[0].rate or 0
            else:
                contract_job.hourly_rate = False

    hourly_rate_class_id = fields.Many2one('hr.hourly.rate.class',
                                           string='Hourly Rate Class')
    hourly_rate = fields.Float(string='Hourly Rate',
                               compute="_get_current_hourly_rate")
