# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrPersonalEquipmentRequest(models.Model):

    _inherit = "hr.personal.equipment.request"

    contains_ppe = fields.Boolean(compute="_compute_contains_ppe")

    def _compute_contains_ppe(self):
        for rec in self:
            for line in rec.line_ids:
                if line.is_ppe:
                    rec.contains_ppe = True
                    return
                else:
                    rec.contains_ppe = False

    def action_view_ppe_report(self):
        report = self.env["ir.actions.report"]._get_report_from_name(
            "hr_employee_ppe.hr_employee_ppe_report_template"
        )
        return report.report_action(self)
