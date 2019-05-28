# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api


class HrContractJob(models.Model):
    _inherit = 'hr.contract.job'

    @api.multi
    def _get_current_hourly_rate(self):
        today = fields.Date.today()
        for contract_job in self:
            contract = contract_job.contract_id
            if contract_job.hourly_rate_class_id and \
                    contract.salary_computation_method == 'hourly':
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
