# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

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
        if self.ongoing_appraisal_count > 1:
            action.update(
                {
                    "name": _("New and Pending Appraisals"),
                    "view_mode": "tree,form",
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
                    "res_id": self.last_appraisal_id.id,
                }
            )
        return action

    def _search_last_appraisal_id(self, operator, value):
        appraisals = self.env["hr.appraisal"].search([("id", operator, value)])
        return [("id", "in", appraisals.mapped("employee_id").ids)]

    def _compute_last_appraisal_id(self):
        for employee in self:
            last_appraisal = self.env["hr.appraisal"].search(
                [("employee_id", "=", employee.id)],
                order="create_date desc",
                limit=1,
            )
            employee.last_appraisal_id = last_appraisal

    def _compute_can_open_last_appraisal(self):
        """
        Check if the employee has a last appraisal and if the user
        is allowed to open it (HR Officer can see all).
        """
        user = self.env.user
        is_hr_officer = user.has_group("hr_appraisal_oca.group_appraisal_hr_officer")
        for employee in self:
            is_self = employee.user_id and employee.user_id.id == user.id
            allowed = is_hr_officer or user in employee.allowed_user_ids or is_self
            employee.can_open_last_appraisal = bool(
                allowed and employee.last_appraisal_id
            )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    appraisal_count = fields.Integer(
        compute="_compute_appraisal_count",
        store=True,
        groups="hr.group_hr_user",
    )
    appraisal_ids = fields.One2many("hr.appraisal", "employee_id", string="Appraisal")
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
    )

    @api.depends("parent_id")
    def _compute_allowed_user_ids(self):
        """Compute all allowed user IDs by traversing the manager hierarchy."""
        for employee in self:
            allowed_users = set()
            visited = set()
            current = employee.parent_id
            while current and current.id not in visited:
                visited.add(current.id)
                if current.user_id:
                    allowed_users.add(current.user_id.id)
                current = current.parent_id
            employee.allowed_user_ids = [(6, 0, list(allowed_users))]

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
