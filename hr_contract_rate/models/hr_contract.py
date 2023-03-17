# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    wage = fields.Monetary(
        compute="_compute_wage",
        inverse="_inverse_wage",
        store=True,
        required=False,
        track_visibility=None,
    )
    approximate_wage = fields.Monetary(
        string="Wage (approximate)",
        compute="_compute_wage",
        store=True,
        help="Employee's monthly gross wage (approximate)",
    )
    is_wage_accurate = fields.Boolean(
        compute="_compute_wage",
        store=True,
    )
    work_hours_per_month = fields.Float(
        string="Work hours (per month)",
        default=lambda self: self._default_work_hours_per_month(),
        help="How many work hours there is in an average month",
    )
    work_days_per_month = fields.Float(
        string="Work days (per month)",
        default=lambda self: self._default_work_days_per_month(),
        help="How many work days there is in an average month",
    )
    work_weeks_per_month = fields.Float(
        string="Work weeks (per month)",
        default=lambda self: self._default_work_weeks_per_month(),
        help="How many work weeks there is in an average month",
    )
    amount = fields.Monetary(
        string="Amount",
        track_visibility="onchange",
        help="Employee's contract amount per period",
    )
    amount_period = fields.Selection(
        string="Period of Amount",
        selection=[
            ("hour", "Hour"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        default="month",
        track_visibility="onchange",
        help="Period of employee's contract amount",
    )

    @api.model
    def _default_work_hours_per_month(self):
        """Hook for extensions"""
        return 2080.0 / 12.0

    @api.model
    def _default_work_days_per_month(self):
        """Hook for extensions"""
        return self._default_work_hours_per_month() / 8.0

    @api.model
    def _default_work_weeks_per_month(self):
        """Hook for extensions"""
        return self._default_work_days_per_month() / 5.0

    def _get_wage_from_amount(self):
        """Hook for extensions"""
        self.ensure_one()
        if self.amount_period == "hour":
            is_wage_accurate = False
            wage = self.amount * self.work_hours_per_month
        elif self.amount_period == "day":
            is_wage_accurate = False
            wage = self.amount * self.work_days_per_month
        elif self.amount_period == "week":
            is_wage_accurate = False
            wage = self.amount * self.work_weeks_per_month
        elif self.amount_period == "month":
            is_wage_accurate = True
            wage = self.amount
        elif self.amount_period == "quarter":
            is_wage_accurate = True
            wage = self.amount / 3.0
        elif self.amount_period == "year":
            is_wage_accurate = True
            wage = self.amount / 12.0
        return wage, is_wage_accurate

    @api.depends(
        "amount",
        "amount_period",
        "work_hours_per_month",
        "work_days_per_month",
        "work_weeks_per_month",
    )
    def _compute_wage(self):
        for contract in self:
            wage, is_wage_accurate = contract._get_wage_from_amount()
            contract.is_wage_accurate = is_wage_accurate
            contract.approximate_wage = 0 if is_wage_accurate else wage
            contract.wage = wage if is_wage_accurate else 0

    def _inverse_wage(self):
        if self.env.context.get("hr_contract_inverse_wage_skip"):
            return

        # NOTE: In order to maintain compatibility with other tests also
        # support setting monthly amount by setting wage directly.
        for contract in self:
            if contract.amount != contract.wage:
                contract.amount = contract.wage
            if contract.amount_period != "month":
                contract.amount_period = "month"
