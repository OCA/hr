# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class HrHolidays(models.Model):

    _inherit = 'hr.holidays'

    @api.onchange('date_from', 'employee_id')
    def _onchange_date_from(self):
        super(HrHolidays, self)._onchange_date_from()
        self.number_of_days_temp = \
            len(
                self.env['hr.holidays.public']
                    ._compute_date(
                        self.date_from,
                        self.date_to,
                        self.employee_id
                )['annual_leaves']
            )

    @api.onchange('date_to', 'employee_id')
    def _onchange_date_to(self):
        super(HrHolidays, self)._onchange_date_to()
        self.number_of_days_temp = \
            len(
                self.env['hr.holidays.public']
                    ._compute_date(
                        self.date_from,
                        self.date_to,
                        self.employee_id
                )['annual_leaves']
            )
