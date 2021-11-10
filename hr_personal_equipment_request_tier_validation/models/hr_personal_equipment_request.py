# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HrPersonalEquipmentRequest(models.Model):

    _name = "hr.personal.equipment.request"
    _inherit = ["hr.personal.equipment.request", "tier.validation"]
    _tier_validation_manual_config = False
    _tier_validation_buttons_xpath = "/form/header/button[last()-1]"

    _state_to = ["accepted"]
    _cancel_state = "cancelled"
