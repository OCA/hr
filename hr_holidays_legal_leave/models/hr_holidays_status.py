# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    is_annual = fields.Boolean(
        'Legal/Annual',
        compute='_compute_is_annual',
        inverse='_inverse_is_annual',
        help='Use this Leave type as Legal/Annual for current company. '
             'One and only one leave type can have this checkbox. '
             'You cannot unset it directly. '
             'Set it on another Leave type instead. '
    )

    @api.multi
    def _compute_is_annual(self):
        company = self.env.user.company_id
        self.filtered(lambda x: x == company.legal_holidays_status_id)\
            .update({'is_annual': True})

    @api.multi
    def _inverse_is_annual(self):
        self.ensure_one()
        company = self.env.user.company_id
        if self.is_annual:
            company.legal_holidays_status_id = self.id
