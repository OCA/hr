# Copyright 2020 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HrContract(models.Model):
    _inherit = "hr.contract"

    # defuse this, it makes no sense when this module is active
    def _compute_calendar_mismatch(self):
        return False
