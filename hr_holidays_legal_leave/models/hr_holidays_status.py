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
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self._get_default_company()
    )

    def _get_default_company(self):
        return self.env.user.company_id.id

    @api.depends('company_id')
    def _compute_is_annual(self):
        for rec in self:
            rec.is_annual = rec.company_id.legal_holidays_status_id == rec.id

    @api.multi
    def _inverse_is_annual(self):
        self.ensure_one()
        if self.is_annual:
            self.company_id.legal_holidays_status_id = self.id
