from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_role_manager(self):
        self.ensure_one()
        # find the manager independently of the currently selected company
        employees = (
            self.env["hr.employee"]
            .sudo()
            .search([("user_id", "=", self.id), ("parent_id", "!=", False)])
        )
        employee = (
            employees.filtered(lambda e: e.company_id == self.env.company)[:1]
            or employees[:1]
        )
        return employee.parent_id.user_id or super()._get_role_manager()
