# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    @api.multi
    @api.constrains('holiday_status_id')
    def _check_leave_type_validity(self):
        super(
            HolidaysAllocation,
            self.filtered('holiday_status_id.restrict_dates')
        )._check_leave_type_validity()
