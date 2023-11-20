# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def find_hr_period(self, date):
        """
        try to find a date range with type 'hr_period'
        with @param:date contained in its date_start/date_end interval
        """
        hr_period = self.env["hr.period"].search(
            [
                ("company_id", "=", self.id),
                ("date_start", "<=", date),
                ("date_end", ">=", date),
            ],
            limit=1,
        )

        return hr_period
