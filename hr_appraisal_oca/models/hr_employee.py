# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import SQL


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    appraisal_count = fields.Integer(
        compute="_compute_appraisal_count",
        store=True,
        groups="hr.group_hr_user",
    )
    appraisal_ids = fields.One2many("hr.appraisal", "employee_id")
    last_appraisal_state = fields.Selection(
        related="last_appraisal_id.state", string="Status"
    )
    ongoing_appraisal_count = fields.Integer(
        compute="_compute_ongoing_appraisal_count",
        store=True,
        groups="hr.group_hr_user",
    )
    allowed_user_ids = fields.Many2many(
        "res.users",
        relation="hr_employee_manager_user_rel",
        column1="employee_id",
        column2="user_id",
        string="Allowed Users",
        compute="_compute_allowed_user_ids",
        store=True,
        recursive=True,
    )
    last_appraisal_id = fields.Many2one(
        "hr.appraisal",
        compute="_compute_last_appraisal_id",
        search="_search_last_appraisal_id",
    )
    can_open_last_appraisal = fields.Boolean(compute="_compute_can_open_last_appraisal")

    def action_open_last_appraisal(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "res_model": "hr.appraisal",
            "context": dict(self.env.context, default_employee_id=self.id),
        }
        ongoing_appraisals = self.env["hr.appraisal"].search(
            [("employee_id", "=", self.id), ("state", "in", ["1_new", "2_pending"])],
            order="create_date desc, id desc",
            limit=2,
        )
        if len(ongoing_appraisals) > 1:
            action.update(
                {
                    "name": self.env._("New and Pending Appraisals"),
                    "view_mode": "list,form",
                    "domain": [
                        ("employee_id", "=", self.id),
                        ("state", "!=", "3_done"),
                    ],
                }
            )
        else:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": (ongoing_appraisals or self.last_appraisal_id).id,
                }
            )
        return action

    def _search_last_appraisal_id(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        latest = self._get_last_appraisal_ids([])
        if False in value:
            # Employees without accessible appraisals also match False.
            employee_ids = [
                employee_id
                for employee_id, appraisal_id in latest.items()
                if appraisal_id not in value
            ]
            domain_operator = "not in" if operator == "in" else "in"
        else:
            employee_ids = [
                employee_id
                for employee_id, appraisal_id in latest.items()
                if appraisal_id in value
            ]
            domain_operator = operator
        return [("id", domain_operator, employee_ids)]

    @api.model
    def _get_last_appraisal_ids(self, domain):
        """Return one appraisal ID per employee, applying appraisal access rules."""
        query = self.env["hr.appraisal"]._search(domain)
        if query.is_empty():
            return {}
        table = query.table
        query.order = SQL(
            "%s, %s DESC, %s DESC", table.employee_id, table.create_date, table.id
        )
        return dict(
            self.env.execute_query(
                query.select(
                    SQL("DISTINCT ON (%s) %s", table.employee_id, table.employee_id),
                    table.id,
                )
            )
        )

    @api.depends_context("uid")
    @api.depends("appraisal_ids", "appraisal_ids.create_date")
    def _compute_last_appraisal_id(self):
        latest = self._get_last_appraisal_ids([("employee_id", "in", self.ids)])
        Appraisal = self.env["hr.appraisal"]
        for employee in self:
            employee.last_appraisal_id = Appraisal.browse(latest.get(employee.id))

    @api.depends_context("uid")
    @api.depends("last_appraisal_id")
    def _compute_can_open_last_appraisal(self):
        """The last appraisal search already applies the user's access rules."""
        for employee in self:
            employee.can_open_last_appraisal = bool(employee.last_appraisal_id)

    @api.depends("parent_id.allowed_user_ids", "parent_id.user_id")
    def _compute_allowed_user_ids(self):
        """Propagate manager users through the complete hierarchy."""
        for employee in self:
            employee.allowed_user_ids = (
                employee.parent_id.user_id | employee.parent_id.allowed_user_ids
            )

    @api.depends("appraisal_ids")
    def _compute_appraisal_count(self):
        for employee in self:
            employee.appraisal_count = len(employee.appraisal_ids)

    @api.depends("appraisal_ids.state")
    def _compute_ongoing_appraisal_count(self):
        for employee in self:
            employee.ongoing_appraisal_count = len(
                employee.appraisal_ids.filtered(
                    lambda a: a.state in ["1_new", "2_pending"]
                )
            )
