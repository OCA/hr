# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError

org_chart_classes = {
    0: "level-0",
    1: "level-1",
    2: "level-2",
    3: "level-3",
    4: "level-4",
}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot assign manager recursively."))

    def _get_employee_domain(self, parent_id):
        company = self.env.company
        domain = ["|", ("company_id", "=", False), ("company_id", "=", company.id)]
        if not parent_id:
            domain.extend([("parent_id", "=", False), ("child_ids", "!=", False)])
        else:
            domain.append(("parent_id", "=", parent_id))
        return domain

    def _get_employee_data(self, level=0):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.job_id.name,
            "className": org_chart_classes[level],
            "image": self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "hr.employee"),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "image_512"),
                ],
                limit=1,
            )
            .datas,
        }

    @api.model
    def _get_children_data(self, child_ids, level):
        children = []
        for employee in child_ids:
            data = employee._get_employee_data(level)
            employee_child_ids = self.search(self._get_employee_domain(employee.id))
            if employee_child_ids:
                data.update(
                    {
                        "children": self._get_children_data(
                            employee_child_ids, (level + 1) % 5
                        )
                    }
                )
            children.append(data)
        return children

    @api.model
    def get_organization_data(self):
        # First get employee with no manager
        domain = self._get_employee_domain(False)
        data = {"id": None, "name": "", "title": "", "children": []}
        top_employees = self.search(domain)
        for top_employee in top_employees:
            child_data = top_employee._get_employee_data()
            # If any child we fetch data recursively for childs of top employee
            top_employee_child_ids = self.search(
                self._get_employee_domain(top_employee.id)
            )
            if top_employee_child_ids:
                child_data.update(
                    {"children": self._get_children_data(top_employee_child_ids, 1)}
                )
            data.get("children").append(child_data)
        return data
