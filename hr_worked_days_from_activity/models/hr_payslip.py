# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class HrPayslipWorkedDays(models.Model):
    _inherit = "hr.payslip.worked_days"

    import_from_activity = fields.Boolean(
        string="Import from Activity",
    )


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    timesheet_account_ids = fields.Many2many(
        string="Timesheet Account",
        comodel_name="account.analytic.account",
        domain=[("use_timesheets", "=", True)],
        relation="rel_payslip_rule_2_analytic_account",
        column1="rule_id",
        column2="analytic_account_id",
    )


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def action_import_timesheet_activity(self):
        obj_uom = self.env["product.uom"]
        obj_timesheet_line = self.env["hr.analytic.timesheet"]
        obj_worked_days = self.env["hr.payslip.worked_days"]

        for payslip in self:
            res = {}
            uom_hour = self.env.ref("product.product_uom_hour")

            if payslip.state != "draft":
                raise UserError(
                    _("Cannot import timesheet activity on non-draft payslip"))

            criteria = [
                ("payslip_id", "=", payslip.id),
                ("import_from_activity", "=", True),
            ]

            obj_worked_days.search(criteria).unlink()

            if not payslip.employee_id.user_id:
                continue

            user = payslip.employee_id.user_id

            if not payslip.contract_id:
                continue

            for rule in payslip.contract_id.struct_id.rule_ids:
                if not rule.timesheet_account_ids:
                    continue

                wd_code = "TS%s" % rule.code
                wd_code = wd_code.replace(".", "")

                res = {
                    "name": _("Timesheet activities for %s") % rule.name,
                    "code": wd_code,
                    "contract_id": payslip.contract_id.id,
                    "number_of_hours": 0.0,
                    "payslip_id": payslip.id,
                    "import_from_activity": True,
                }

                for account in rule.timesheet_account_ids:
                    criteria = [
                        ("account_id", "child_of", account.id),
                        ("user_id", "=", user.id),
                        ("sheet_id.state", "=", "done"),
                        ("date", ">=", payslip.date_from),
                        ("date", "<=", payslip.date_to),
                    ]
                    for ts_line in obj_timesheet_line.search(
                            criteria):
                        ts_line_hour = obj_uom._compute_qty(
                            ts_line.product_uom_id.id,
                            ts_line.unit_amount,
                            uom_hour.id
                        )
                        res["number_of_hours"] += ts_line_hour
                obj_worked_days.create(res)
