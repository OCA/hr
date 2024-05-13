# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def search(self, args, offset=0, limit=None, order=None, count=False):
        params = self.env.context.get("params")
        if params:
            model = params.get("model")
            if not self.env.context.get("by_pass"):
                if (
                    model in ["hr.leave", "hr.leave.allocation"]
                    and self.env.user.has_group("hr_holidays.group_hr_holidays_user")
                    and not self.env.user.has_group(
                        "hr_holidays_team_manager.group_hr_holidays_officer"
                    )
                ):
                    if args is None:
                        args = []
                    employee_id = self.env.user.with_context(by_pass=True).employee_ids
                    if employee_id:
                        args += [
                            ("department_id", "=", employee_id[0].department_id.id)
                        ]

        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        context = self.env.context
        if context:
            if not self.env.context.get("by_pass"):
                if (
                    [context.get("hr_leave_allocation") or context.get("hr_leave")]
                    and self.env.user.has_group("hr_holidays.group_hr_holidays_user")
                    and not self.env.user.has_group(
                        "hr_holidays_team_manager.group_hr_holidays_officer"
                    )
                ):
                    if args is None:
                        args = []
                    employee_id = self.env.user.with_context(by_pass=True).employee_ids
                    if employee_id:
                        args += [
                            ("department_id", "=", employee_id[0].department_id.id)
                        ]

        return super().name_search(name=name, args=args, operator=operator, limit=limit)
