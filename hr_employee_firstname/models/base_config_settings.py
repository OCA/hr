# Copyright 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    employee_names_order = fields.Selection(
        selection="_employee_names_order_selection",
        help="Order to compose employee fullname",
        config_parameter="employee_names_order",
        default=lambda a: a._employee_names_order_default(),
        required=True,
    )

    def _employee_names_order_selection(self):
        return [
            ("last_first", "Lastname Firstname"),
            ("last_first_comma", "Lastname, Firstname"),
            ("first_last", "Firstname Lastname"),
        ]

    def _employee_names_order_default(self):
        return self.env["hr.employee"]._names_order_default()
