from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.onchange("request_date_from", "request_date_to", "employee_id")
    def _onchange_update_visual_hours(self):
        for leave in self:
            if not (
                leave.employee_id
                and leave.request_date_from
                and leave.employee_id.calendar_ids
            ):
                continue
            check_date = leave.request_date_from
            plans = leave.employee_id.calendar_ids.filtered(
                lambda c, d=check_date: (not c.date_start or c.date_start <= d)
                and (not c.date_end or c.date_end >= d)
            )

            if not plans:
                continue
            best_plan = min(
                plans,
                key=lambda c: (c.date_end - c.date_start).days
                if c.date_start and c.date_end
                else 9999,
            )
            day_str = str(check_date.weekday())
            work_hours = best_plan.calendar_id.attendance_ids.filtered(
                lambda a, d=day_str: a.dayofweek == d and a.day_period != "lunch"
            )
            if work_hours:
                leave.request_hour_from = min(work_hours.mapped("hour_from"))
                leave.request_hour_to = max(work_hours.mapped("hour_to"))
