# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # In Odoo 19, hr.contract was replaced by hr.version (contract dates live there).
    first_contract_id = fields.Many2one(
        "hr.version",
        compute="_compute_first_contract_id",
        store=True,
        prefetch=False,
        string="First Contract",
        help="First contract of the employee",
    )
    last_contract_id = fields.Many2one(
        "hr.version",
        compute="_compute_last_contract_id",
        store=True,
        prefetch=False,
        string="Last Contract",
        help="Last contract of the employee",
    )
    service_start_date = fields.Date(
        string="Start Date",
        readonly=True,
        related="first_contract_id.contract_date_start",
        prefetch=False,
    )
    service_termination_date = fields.Date(
        string="Termination Date",
        readonly=True,
        related="last_contract_id.contract_date_end",
        prefetch=False,
    )

    @api.depends(
        "version_ids",
        "version_ids.contract_date_start",
    )
    def _compute_first_contract_id(self):
        Version = self.env["hr.version"]
        for employee in self:
            employee.first_contract_id = Version.search(
                employee._get_contract_filter(),
                order="contract_date_start asc",
                limit=1,
            )

    @api.depends(
        "version_ids",
        "version_ids.contract_date_end",
        "version_ids.contract_date_start",
    )
    def _compute_last_contract_id(self):
        Version = self.env["hr.version"]
        for employee in self:
            # Open-ended contracts (no end date) sort first with DESC in PostgreSQL
            # (NULLS FIRST), matching former "open"/"close without end" behaviour.
            employee.last_contract_id = Version.search(
                employee._get_contract_filter(),
                order="contract_date_end desc",
                limit=1,
            )

    @api.onchange("service_hire_date")
    def _onchange_service_hire_date(self):  # pragma: no cover
        # Do nothing — service dates come from contracts/versions.
        pass

    def _get_contract_filter(self):
        self.ensure_one()
        return [
            ("employee_id", "=", self.id),
            ("contract_date_start", "!=", False),
        ] + self._get_service_contract_domain()

    @api.model
    def _get_service_contract_domain(self):
        """Extension hook for extra domain on versions counted as contracts.

        Replaces ``_get_service_contract_states`` from previous versions: contract
        states (open/pending/close) no longer exist on ``hr.version``.
        """
        return []
