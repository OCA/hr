# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

TYPE_SELECTION = [
    ("contract", _("Contract")),
    ("leave", _("Leave")),
    ("timesheet", _("Timesheet")),
]

_logger = logging.getLogger(__name__)


def get_end_of_day(date, attendances):
    """ Returns the datetime corresponding to the end of the day """
    hour_from = 0.0
    hour_to = 0.0
    for attendance in attendances:
        if not hour_from or hour_from > attendance.hour_from:
            hour_from = attendance.hour_from
        if not hour_to or hour_to < attendance.hour_to:
            hour_to = attendance.hour_to
    return datetime.datetime.combine(date, odoo_float_time_to_datetime_time(hour_to))


def odoo_float_time_to_datetime_time(dec_hour):
    """Transform a decimal time representation to a time object
    For instance: 2.25 hours into datetime.Time(2, 15, 0)
    """

    def frac(n):
        """Split value in two sexadecimal units
        For instance: 2.25 hours into 2 hours and 15 minutes
        """
        i = int(n)
        f = round((n - int(n)), 4)
        return (i, f)

    hours, _min = frac(dec_hour)
    minutes, _sec = frac(_min * 60)
    seconds, _msec = frac(_sec * 60)
    return datetime.time(hours, minutes, seconds)


def generate_dates_from_range(start_date, end_date=None):
    """ Prepare a list of date to be processed """
    if not end_date:
        end_date = fields.Date().today()
    return [
        start_date + relativedelta(days=x)
        for x in range((end_date - start_date).days + 1)
    ]


class HrEmployeeHour(models.Model):
    _name = "hr.employee.hour"
    _description = "HR Employee Hours per day"
    _order = "date"

    date = fields.Date("Date", readonly=True, required=True)
    name = fields.Char("Description", readonly=True, required=True)
    type = fields.Selection(
        TYPE_SELECTION, string="Type", default="contract", required=True
    )
    sum_type = fields.Selection(
        [
            ("add", "Add"),
            ("remove", "Remove"),
        ]
    )
    unplanned = fields.Boolean("Unplanned", default=False)
    hours_qty = fields.Float("Hours Qty", readonly=True, required=True)
    days_qty = fields.Float("Day Qty", readonly=True, required=True)
    percentage = fields.Float("Percentage")
    employee_id = fields.Many2one("hr.employee", readonly=True, required=True)
    manager_id = fields.Many2one(
        "hr.employee", related="employee_id.parent_id", store=True
    )
    user_id = fields.Many2one("res.users", related="employee_id.user_id", store=True)
    company_id = fields.Many2one(
        "res.company", related="employee_id.company_id", store=True
    )
    project_id = fields.Many2one("project.project")
    analytic_group_id = fields.Many2one("account.analytic.group")
    model_name = fields.Char("Model Name", readonly=True, required=True)
    res_id = fields.Integer("Ressource ID", readonly=True, required=True)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        # Add the percentage values
        # Force addition of this fields if not in the view specification
        needed_fields = ["hours_qty", "hours_qty:sum"]
        if not set(fields).intersection(set(needed_fields)):
            fields.append("hours_qty:sum")
        result = super().read_group(
            domain, fields, groupby, offset, limit, orderby, lazy
        )

        if not result or not len(result) > 1:
            # Avoid processing if empty or only one result
            return result

        def get_grant_total(groups, key):
            """ Return the sum of this key's values for all records """
            return sum([rec.get(key, 0.0) for rec in groups])

        hours_total = get_grant_total(result, "hours_qty")
        for rec in result:
            if hours_total:
                rec["percentage"] = (rec.get("hours_qty", 0.0) / hours_total) * 100
        return result

    @api.model
    def get_time_quantities_from_calendar(self, calendar, attendances=None):
        """Process each attendance by summing morning and afternoon hours
        and defining day percentage correspondingly (0.5 if only morning,
        1.0 if both).

        By default, hours_per_day from calendar is returned and 1 full day.
        """
        hours_qty = days_qty = 0.0
        if not attendances:
            attendances = []
        for attendance in attendances:
            hours_qty += attendance.hour_to - attendance.hour_from
            if attendance.day_period == "morning":
                days_qty += 0.5
            elif attendance.day_period == "afternoon":
                days_qty += 0.5
        return hours_qty or calendar.hours_per_day, days_qty or 1.0

    @api.model
    def _prepare_attendance_value(self, contract, date, exclude_global_leaves=True):
        """Returns attendance values for this date

        This attendance is a matrix product of contractual hours by day
        and week days for this date (NOT the `hr.attendance` model).

        :param employee: an employee record
        :param date_from: a datetime.date
        :param exclude_global_leaves: Do not include global leave at date
        """
        values = {}
        calendar = contract.resource_calendar_id
        attendances = calendar.attendance_ids.filtered(
            lambda att: int(att.dayofweek) == date.weekday()
        )
        # Here, we MUST use datetime as some global leaves are based
        # on the previous day at 23h mostly
        end_of_day = get_end_of_day(date, attendances)
        global_leaves = calendar.global_leave_ids.filtered(
            lambda gl: gl.date_from <= end_of_day <= gl.date_to
        )
        # We only take valid days of work
        if attendances and (not global_leaves or exclude_global_leaves):
            hours_qty, days_qty = self.get_time_quantities_from_calendar(
                calendar, attendances
            )
            values = {
                "name": contract.name,
                "model_name": "hr.contract",
                "res_id": contract.id,
                "date": date,
                "employee_id": contract.employee_id.id,
                "type": "contract",
                "hours_qty": -hours_qty,
                "days_qty": -days_qty,
                "sum_type": "remove",
            }
        return values

    @api.model
    def _get_attendances_values(self, employee, date_from):
        """Retrieve attendances (from resource module) values mapped by date

        These attendances are the matrix product of contractual hours by day
        and week days (NOT the `hr.attendance` model).

        Warning: it is intended to be injected in context to reduce calls

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        date_to = fields.Date.today()
        values_by_date = {}
        for contract in employee.contract_ids:
            _logger.debug(
                f"""process contract '{contract.name}'
                from {contract.last_hours_report_date} to {date_to}"""
            )
            ranged_dates = generate_dates_from_range(
                contract.last_hours_report_date, date_to
            )
            for date in ranged_dates:
                if date_from <= date >= date_to:
                    continue
                values = self._prepare_attendance_value(contract, date)
                if values:
                    values_by_date[date] = values
        return list(values_by_date.values())

    @api.model
    def _hook_get_type_from_timesheet(self, timesheet):
        """Hook to allow proper override of type value
        Called in `_prepare_timesheets_lines` method
        """
        return "leave" if timesheet.holiday_id else "timesheet"

    @api.model
    def _hook_get_name_from_timesheet(self, timesheet):
        """Hook to allow proper override of name value
        Called in `_prepare_timesheets_lines` method
        """
        return timesheet.account_id.name if timesheet.holiday_id else timesheet.name

    def _prepare_timesheet_line(self, timesheet):
        """Retrieve a timesheet line values

        Day ratio quantity is a percentage of consumed hours relative to the
        attendance day max quantity to make a full day (2h on 8h day is 25%).

        If `attendances_by_date` is not set in context or date is not found,
        default hours and day quantity are used (cf: `DEFAULT_TIME_QTY`)

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        """
        uom_hour = self.env.ref("uom.product_uom_hour")
        project = timesheet.project_id
        hours_qty = timesheet.unit_amount
        if timesheet.product_uom_id != uom_hour:
            hours_qty = timesheet.product_uom_id._compute_quantity(
                timesheet.unit_amount, uom_hour, round=False
            )

        # TODO?
        # If attendance hours qty is empty, it is an extra work day
        days_qty = hours_qty / timesheet.employee_id.resource_calendar_id.hours_per_day

        values = {
            "name": self._hook_get_name_from_timesheet(timesheet),
            "type": self._hook_get_type_from_timesheet(timesheet),
            "model_name": timesheet._name,
            "res_id": timesheet.id,
            "date": timesheet.date,
            "employee_id": timesheet.employee_id.id,
            "project_id": project.id,
            "analytic_group_id": timesheet.group_id.id,
            "hours_qty": hours_qty,
            "days_qty": days_qty,
            "sum_type": "add",
        }
        return values

    @api.model
    def _prepare_timesheets_lines(self, employee, date_from):
        """Retrieve all timesheets values

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        """
        aal_model = self.env["account.analytic.line"]
        timesheets = aal_model.search(
            [
                ("employee_id", "=", employee.id),
                ("project_id", "!=", False),
                ("unit_amount", "!=", 0.0),
                ("date", ">=", date_from),
            ]
        )
        values_list = []
        for timesheet in timesheets:
            values = self._prepare_timesheet_line(timesheet)
            if values:
                values_list.append(values)
        return values_list

    @api.model
    def action_generate_data(self, employee_ids=None):
        """Launch update process
        In case of force update, we unlink all related lines and reprocess them
        completely

        :param employee_ids: a list of employee ids
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        :param force: purge all lines related to params before regenerating
        """
        employees = self.env["hr.employee"].browse(employee_ids)
        employees = employees.filtered(lambda emp: emp.last_hours_report_date)
        if not employees:
            employees = self.env["hr.employee"].search(
                [
                    ("last_hours_report_date", "!=", False),
                ]
            )

        for employee in employees:
            date_from = employee.last_hours_report_date
            existing_lines = self.search(
                [
                    ("employee_id", "=", employee.id),
                    ("date", ">=", date_from),
                ]
            )
            if existing_lines:
                _logger.info(f"Purge hours for '{employee.name}' from {date_from}")
                existing_lines.unlink()
            _logger.info(f"Generating hours for '{employee.name}' from {date_from}")
            self._create_values_per_employee(employee, date_from)
            employee.contract_ids.update(
                {"last_hours_report_date": fields.Date.today()}
            )

    def _create_values_per_employee(self, employee, date):
        att_vals = self._get_attendances_values(employee, date)
        ts_vals = self._prepare_timesheets_lines(employee, date)
        self.create(att_vals + ts_vals)
