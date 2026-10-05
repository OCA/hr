# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

# An average work year of 2080 hours (40 h/week x 52 weeks), 8 h days and
# 5-day weeks. Overridable through the hooks below for other calendars.
WORK_HOURS_PER_YEAR = 2080.0
MONTHS_PER_YEAR = 12.0
WORK_HOURS_PER_DAY = 8.0
WORK_DAYS_PER_WEEK = 5.0
MONTHS_PER_QUARTER = 3.0

#: Periods a contract amount can be quoted in. Exported so that models whose
#: amounts are copied onto the contract (a pay scale, for instance) can share
#: the very same keys.
AMOUNT_PERIOD_SELECTION = [
    ("hour", "Hour"),
    ("day", "Day"),
    ("week", "Week"),
    ("month", "Month"),
    ("quarter", "Quarter"),
    ("year", "Year"),
]


class HrContract(models.Model):
    _inherit = "hr.contract"

    # Core declares ``wage`` as the monthly gross wage. Here it is derived
    # from the rate instead of typed in, and stays writable through the
    # inverse. The rate fields are the ones tracked.
    wage = fields.Monetary(
        compute="_compute_wage",
        inverse="_inverse_wage",
        store=True,
        required=False,
        tracking=False,
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
        tracking=True,
        help="Employee's contract amount per period",
    )
    amount_period = fields.Selection(
        string="Period of Amount",
        selection=AMOUNT_PERIOD_SELECTION,
        default="month",
        tracking=True,
        help="Period of employee's contract amount",
    )

    @api.model
    def _default_work_hours_per_month(self):
        """Hook for extensions"""
        return WORK_HOURS_PER_YEAR / MONTHS_PER_YEAR

    @api.model
    def _default_work_days_per_month(self):
        """Hook for extensions"""
        return self._default_work_hours_per_month() / WORK_HOURS_PER_DAY

    @api.model
    def _default_work_weeks_per_month(self):
        """Hook for extensions"""
        return self._default_work_days_per_month() / WORK_DAYS_PER_WEEK

    def _get_wage_from_amount(self):
        """Return ``(monthly_wage, is_accurate)`` for this contract's rate.

        Hourly, daily and weekly rates can only be estimated, because the real
        monthly total depends on how much the employee actually works.

        Hook for extensions.
        """
        self.ensure_one()
        estimated_factors = {
            "hour": self.work_hours_per_month,
            "day": self.work_days_per_month,
            "week": self.work_weeks_per_month,
        }
        if self.amount_period in estimated_factors:
            return self.amount * estimated_factors[self.amount_period], False
        exact_factors = {
            "month": 1.0,
            "quarter": 1.0 / MONTHS_PER_QUARTER,
            "year": 1.0 / MONTHS_PER_YEAR,
        }
        return self.amount * exact_factors.get(self.amount_period, 0.0), True

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
            contract.approximate_wage = 0.0 if is_wage_accurate else wage
            contract.wage = wage if is_wage_accurate else 0.0

    def _inverse_wage(self):
        if self.env.context.get("hr_contract_inverse_wage_skip"):
            return

        # NOTE: In order to maintain compatibility with other modules and
        # their tests, also support setting a monthly amount by setting the
        # wage directly.
        for contract in self:
            if contract.amount != contract.wage:
                contract.amount = contract.wage
            if contract.amount_period != "month":
                contract.amount_period = "month"
