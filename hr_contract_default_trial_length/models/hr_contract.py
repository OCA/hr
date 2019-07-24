# Copyright 2015 Salton Massally
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.onchange('type_id')
    @api.multi
    def onchange_trial_date_start(self):
        self.ensure_one()
        self.trial_date_end = False
        if self.date_start and self.type_id:
            days = self.type_id.trial_length
            if days:
                end_dt = fields.Date.from_string(
                    self.date_start) + relativedelta(days=days)
                self.trial_date_end = fields.Date.to_string(end_dt)
