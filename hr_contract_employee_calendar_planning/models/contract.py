from odoo import api, models


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

    @api.model_create_multi
    def create(self, vals_list):
        # the create method of contracts syncs contract calendars with employee calendars
        # in order to not overwrite the employee calendar
        # we set the contract calendar to match the employee calendar
        for vals in vals_list:
            employee_contract = (
                self.env["hr.employee"]
                .browse([vals.get("employee_id")])
                .resource_calendar_id
            )
            if employee_contract:
                vals.update({"resource_calendar_id": employee_contract.id})
        return super().create(vals_list)
