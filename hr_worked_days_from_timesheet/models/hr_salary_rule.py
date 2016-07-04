# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


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
