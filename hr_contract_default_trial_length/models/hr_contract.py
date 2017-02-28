# -*- coding: utf-8 -*-
# Copyright 2015 Salton Massally
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.onchange('trial_date_start', 'type_id')
    @api.multi
    def onchange_trial_date_start(self):
        self.ensure_one()
        if self.trial_date_start and len(self.type_id):
            res = self.type_id.trial_length
            if res:
                end_dt = fields.Date.from_string(
                    self.trial_date_start) + relativedelta(days=res)
                self.trial_date_end = fields.Date.to_string(end_dt)
