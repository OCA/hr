# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.config.settings'

    legal_holidays_status_id = fields.Many2one(
        'hr.holidays.status',
        'Legal Leave Status',
    )

    @api.model
    def get_legal_holidays_status_id(self):
        company = self.env.user.company_id
        return {
            'legal_holidays_status_id': company.legal_holidays_status_id.id,
        }

    @api.multi
    def set_legal_holidays_status_id(self):
        self.ensure_one()
        company = self.env.user.company_id
        company.legal_holidays_status_id = self.legal_holidays_status_id
