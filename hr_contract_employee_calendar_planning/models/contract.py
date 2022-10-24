from odoo import models


class HrContract(models.Model):
    _inherit = "hr.contract"

    def write(self, vals):
        if (
            vals.get("resource_calendar_id")
            and self.employee_id
            and vals.get("resource_calendar_id")
            != self.employee_id.resource_calendar_id.id
        ):
            # in the write method of contracts, when writing the resource_calendar_id
            # the employee resource_calendar_id is set to the same id
            # this interferes with the logic of hr_employee_calendar_planning
            # which assumes that calendar times are managed by resource.calendar.attendances
            # in auto-generated calendars based on the employee's calendar_ids
            # since the default calendar for new contracts is the employee calendar
            # and we set the correct calendar for the existing contract in the post_init_hook
            # we resolve this conflict by not allowing calendar changes in contracts
            vals.pop("resource_calendar_id")
        return super().write(vals)
