# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class Contract(models.Model):
    _inherit = "hr.contract"

    def write(self, values):
        result = super().write(values)
        self.env["hr.employee.hour"].search(
            [
                ("employee_id", "in", self.mapped("employee_id.id")),
                ("model_name", "=", self._name),
                ("res_id", "in", self.ids),
            ]
        ).write({"is_invalidated": True})
        return result
