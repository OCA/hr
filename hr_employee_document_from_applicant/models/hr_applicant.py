# Copyright (C) 2024 Open Source Integrators (https://www.opensourceintegrators.com)
# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def create_employee_from_applicant(self):
        action = super().create_employee_from_applicant()
        if action.get("res_id"):
            employee = self.env["hr.employee"].browse(action["res_id"])
            applicant_attachments = (
                self.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", "hr.applicant"),
                        ("res_id", "=", self.id),
                    ]
                )
            )
            for attachment in applicant_attachments:
                attachment.write(
                    {
                        "res_model": "hr.employee",
                        "res_id": employee.id,
                    }
                )
        return action
