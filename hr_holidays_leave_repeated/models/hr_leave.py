# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    repeat_every = fields.Selection(
        [
            ("workday", "Every workday"),
            ("week", "Every week"),
            ("biweek", "Every two weeks"),
            ("month", "Every four weeks"),
        ]
    )
    repeat_mode = fields.Selection(
        [("times", "Number of Times"), ("date", "End Date")], default="times"
    )
    holiday_type_repeat = fields.Boolean(related="holiday_status_id.repeat")
    repeat_limit = fields.Integer(default=1, string="Repeat # times")
    repeat_end_date = fields.Date(default=lambda self: fields.Date.today())

    @api.model
    def _update_repeated_workday_dates(self, employee, from_dt, to_dt, days):
        user = self.env.user
        calendar = employee.resource_calendar_id
        orig_from_dt = fields.Datetime.context_timestamp(user, from_dt)
        orig_to_dt = fields.Datetime.context_timestamp(user, to_dt)
        work_hours = calendar.get_work_hours_count(from_dt, to_dt, compute_leaves=False)
        while work_hours:
            from_dt = from_dt + relativedelta(days=days)
            to_dt = to_dt + relativedelta(days=days)

            new_work_hours = calendar.get_work_hours_count(
                from_dt, to_dt, compute_leaves=True
            )
            if new_work_hours and work_hours <= new_work_hours:
                break

        user_from_dt = fields.Datetime.context_timestamp(user, from_dt)
        user_to_dt = fields.Datetime.context_timestamp(user, to_dt)
        from_dt = from_dt - user_from_dt.tzinfo._utcoffset
        from_dt = from_dt + orig_from_dt.tzinfo._utcoffset
        to_dt = to_dt - user_to_dt.tzinfo._utcoffset
        to_dt = to_dt + orig_to_dt.tzinfo._utcoffset

        return from_dt, to_dt

    @api.model
    def _get_repeated_vals_dict(self):
        return {
            "workday": {
                "days": 1,
                "user_error_msg": _(
                    "The repetition is based on workdays: the duration of "
                    "the leave request must not exceed 1 day."
                ),
            },
            "week": {
                "days": 7,
                "user_error_msg": _(
                    "The repetition is every week: the duration of the "
                    "leave request must not exceed 1 week."
                ),
            },
            "biweek": {
                "days": 14,
                "user_error_msg": _(
                    "The repetition is every two weeks: the duration of the "
                    "leave request must not exceed 2 weeks."
                ),
            },
            "month": {
                "days": 28,
                "user_error_msg": _(
                    "The repetition is every four weeks: the duration of the "
                    "leave request must not exceed 28 days."
                ),
            },
        }

    @api.model
    def _update_repeated_leave_vals(self, vals, employee):
        vals_dict = self._get_repeated_vals_dict()
        param_dict = vals_dict[vals.get("repeat_every")]
        from_dt = fields.Datetime.from_string(vals.get("date_from"))
        to_dt = fields.Datetime.from_string(vals.get("date_to"))
        end_date = fields.Datetime.from_string(vals.get("repeat_end_date"))

        if (to_dt - from_dt).days > param_dict["days"]:
            raise UserError(param_dict["user_error_msg"])

        from_dt, to_dt = self._update_repeated_workday_dates(
            employee, from_dt, to_dt, param_dict["days"]
        )

        vals["request_date_from"] = vals["date_from"] = from_dt
        vals["request_date_to"] = vals["date_to"] = to_dt
        vals["repeat_end_date"] = end_date
        return vals

    @api.model
    def create_repeated_handler(self, vals, employee):
        def _check_repeating(count, vals):
            repeat_mode = vals.get("repeat_mode", "times")
            if repeat_mode == "times" and count < vals.get("repeat_limit", 0):
                return True
            repeat_end_date = vals.get("repeat_end_date", fields.Date.today())
            if repeat_mode == "date" and vals["date_to"] <= repeat_end_date:
                return True
            return False

        count = 1
        vals = self._update_repeated_leave_vals(vals, employee)
        while _check_repeating(count, vals):
            self.with_context(skip_create_handler=True).create(vals)
            count += 1
            vals = self._update_repeated_leave_vals(vals, employee)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        skip_create_handler = self.env.context.get("skip_create_handler")
        all_vals_set = vals.get("repeat_every") and vals.get("repeat_mode")
        if not skip_create_handler and all_vals_set:
            employee = self.env["hr.employee"].browse(vals.get("employee_id"))
            if employee.resource_calendar_id:
                self.create_repeated_handler(vals, employee)
        return res

    @api.constrains("repeat_limit", "repeat_end_date")
    def _check_repeat_limit(self):
        for record in self:
            if record.repeat_mode == "times" and record.repeat_limit < 0:
                raise ValidationError(_("Please set a positive amount of repetitions."))
            if (
                record.repeat_mode == "date"
                and record.repeat_end_date < fields.Date.today()
            ):
                raise ValidationError(_("The Repeat End Date cannot be in the past"))
