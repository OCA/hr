# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def button_import_attendance(self):
        for payslip in self:
            self._import_attendance(payslip)

    @api.model
    def _import_attendance(self, payslip):
        wd_obj = self.env["hr.payslip.worked_days"]
        day_obj = self.env["hr_timesheet_sheet.sheet.day"]
        date_from = payslip.date_from
        date_to = payslip.date_to

        criteria1 = [
            ("payslip_id", "=", payslip.id),
            ("import_from_attendance", "=", True),
        ]
        wd_obj.search(criteria1).unlink()

        res = {
            "name": _("Total Attendance"),
            "code": "ATTN",
            "number_of_days": 0.0,
            "number_of_hours": 0.0,
            "contract_id": payslip.contract_id.id,
            "import_from_attendance": True,
            "payslip_id": payslip.id,
        }

        criteria2 = [
            ("sheet_id.date_from", ">=", date_from),
            ("sheet_id.date_to", "<=", date_to),
            ("sheet_id.employee_id", "=", payslip.employee_id.id),
        ]

        for day in day_obj.search(criteria2):
            if day.total_attendance >= 0.0:
                res["number_of_days"] += 1
                res["number_of_hours"] += day.total_attendance

        wd_obj.create(res)
