# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def action_update_accrual_allocations(self):
        _logger.info('Trigerring accrual leave types update')
        self._update_accrual()
