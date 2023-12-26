# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class HrExpense(models.Model):
    _inherit = "hr.expense"

    hr_period_id = fields.Many2one(
        comodel_name='hr.period',
        string='Period',
        readonly=True,
        store=True,
        compute="_compute_hr_period",
        search="_search_hr_period",
    )

    @api.depends("date", "company_id")
    def _compute_hr_period(self):
        for rec in self:
            company = rec.company_id
            rec.hr_period_id = company and company.find_hr_period(rec.date) or False

    @api.model
    def _search_hr_period(self, operator, value):
        if operator in ("=", "!=", "in", "not in"):
            date_range_domain = [("id", operator, value)]
        else:
            date_range_domain = [("name", operator, value)]

        date_ranges = self.env["hr.period"].search(date_range_domain)

        domain = [("id", "=", -1)]
        for date_range in date_ranges:
            domain = expression.OR(
                [
                    domain,
                    [
                        "&",
                        ("date", ">=", date_range.date_start),
                        ("date", "<=", date_range.date_end),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", date_range.company_id.id),
                    ],
                ]
            )
        return domain
