from odoo import api, models


class HrVersion(models.Model):
    _inherit = "hr.version"

    def write(self, vals):
        if vals.get("resource_calendar_id") and self.filtered(
            lambda version: version.employee_id
            and vals.get("resource_calendar_id")
            != version.employee_id.resource_calendar_id.id
        ):
            # in the write method of versions, when writing the resource_calendar_id
            # the employee resource_calendar_id is set to the same id
            # this interferes with the logic of hr_employee_calendar_planning,
            # which assumes that calendar times are managed by
            # resource.calendar.attendances in auto-generated calendars
            # based on the employee's calendar_ids.
            # since the default calendar for new versions is the employee calendar,
            # and we set the correct calendar for the existing version
            # in the post_init_hook, we resolve this conflict by not allowing
            # calendar changes in versions.
            vals.pop("resource_calendar_id")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # the create method of versions syncs version
        # calendars with employee calendars
        # in order to not overwrite the employee calendar
        # we set the version calendar to match the employee calendar
        for vals in vals_list:
            employee_calendar = (
                self.env["hr.employee"]
                .browse([vals.get("employee_id")])
                .resource_calendar_id
            )
            if employee_calendar:
                vals.update({"resource_calendar_id": employee_calendar.id})
        return super().create(vals_list)
