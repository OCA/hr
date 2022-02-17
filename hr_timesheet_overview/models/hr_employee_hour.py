# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, registry
from odoo.addons.resource.models.resource import HOURS_PER_DAY

TYPE_SELECTION = [
    ("contract", _("Contract")),
    ("leave", _("Leave")),
    ("timesheet", _("Timesheet")),
]
DEFAULT_TIME_QTY = {"hours_qty": HOURS_PER_DAY, "days_qty": 1.0, "type": "default"}

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
    """ Transform a decimal time representation to a time object
    For instance: 2.25 hours into datetime.Time(2, 15, 0)
    """

    def frac(n):
        """ Split value in two sexadecimal units
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


def get_or_default(date, params):
    """ Just a wrapper for dict default getter """
    return params.get(date, DEFAULT_TIME_QTY)


def get_valid_search_fields():
    """ Returns unicity constrained fields for `HrEmployeeHour` """
    return "date", "employee_id", "model_id", "res_id", "type"


class HrEmployeeHour(models.Model):
    _name = "hr.employee.hour"
    _description = "HR Employee Hours per day"
    _rec_name = "name"
    _order = "date"

    active = fields.Boolean("Active", default=True)
    date = fields.Date("Date", readonly=True, required=True)
    name = fields.Char("Description", readonly=True, required=True)
    type = fields.Selection(
        TYPE_SELECTION, string="Type", default="contract", required=True
    )
    unplanned = fields.Boolean("Unplanned", default=False)
    hours_qty = fields.Float("Hours Qty", readonly=True, required=True)
    days_qty = fields.Float("Day Qty", readonly=True, required=True)
    employee_id = fields.Many2one("hr.employee", readonly=True, required=True)
    manager_id = fields.Many2one(
        "hr.employee", related="employee_id.parent_id", store=True
    )
    user_id = fields.Many2one("res.users", related="employee_id.user_id", store=True)
    company_id = fields.Many2one(
        "res.company", related="employee_id.company_id", store=True
    )
    project_id = fields.Many2one("project.project", readonly=True)
    analytic_group_id = fields.Many2one("account.analytic.group", readonly=True)
    model_id = fields.Many2one("ir.model", "Model", readonly=True, ondelete="set null")
    model_name = fields.Char("Model Name", related="model_id.name", store=True)
    res_id = fields.Integer("Ressource ID", readonly=True, required=True)

    is_invalidated = fields.Boolean(
        "Invalidated", default=False, help="Will be reprocessed at next cron execution"
    )

    _sql_constraints = [
        (
            "uniqueness",
            f"UNIQUE({','.join(get_valid_search_fields())})",
            _(
                "You can't have two hour lines with same fields: %s)".format(
                    ",".join(get_valid_search_fields())
                )
            ),
        )
    ]

    @api.model
    def get_time_quantities_from_calendar(self, calendar, attendances=None):
        """ Process each attendance by summing morning and afternoon hours
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
        """ Returns attendance values for this date

        This attendance is a matrix product of contractual hours by day
        and week days for this date (NOT the `hr.attendance` model).

        :param employee: an employee record
        :param date_from: a datetime.date
        :param exclude_global_leaves: Do not include global leave at date
        """
        values = {}
        ir_model = self.env["ir.model"]
        contract_model_id = ir_model.search([("model", "=", "hr.contract")])
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
                "model_id": contract_model_id.id,
                "res_id": contract.id,
                "date": date,
                "employee_id": contract.employee_id.id,
                "type": "contract",
                "hours_qty": hours_qty,
                "days_qty": days_qty,
            }
        return values

    @api.model
    def _get_attendances_values_by_date(
        self, employee, date_from=None, date_to=fields.Date().today()
    ):
        """ Retrieve attendances (from resource module) values mapped by date

        These attendances are the matrix product of contractual hours by day
        and week days (NOT the `hr.attendance` model).

        Warning: it is intended to be injected in context to reduce calls

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        if not date_from:
            date_from = employee.first_contract_date

        values_by_date = {}
        for contract in employee.contract_ids:
            _logger.debug(
                f"process contract '{contract.name}' from {contract.date_start} to {contract.date_end}"
            )
            ranged_dates = generate_dates_from_range(
                contract.date_start, contract.date_end
            )
            for date in ranged_dates:
                if date_from >= date >= date_to:
                    continue
                values = self._prepare_attendance_value(contract, date)
                if values:
                    values_by_date[date] = values
        return values_by_date

    @api.model
    def _hook_get_type_from_timesheet(self, timesheet):
        """ Hook to allow proper override of type value
        Called in `_prepare_timesheets_lines` method
        """
        return "leave" if timesheet.holiday_id else "timesheet"

    @api.model
    def _hook_get_name_from_timesheet(self, timesheet):
        """ Hook to allow proper override of name value
        Called in `_prepare_timesheets_lines` method
        """
        return timesheet.account_id.name if timesheet.holiday_id else timesheet.name

    def _prepare_timesheet_line(self, timesheet):
        """ Retrieve a timesheet line values

        Day ratio quantity is a percentage of consumed hours relative to the
        attendance day max quantity to make a full day (2h on 8h day is 25%).

        If `attendances_by_date` is not set in context or date is not found,
        default hours and day quantity are used (cf: `DEFAULT_TIME_QTY`)

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        ir_model = self.env["ir.model"]
        aal_model_id = ir_model.search([("model", "=", timesheet._name)])
        uom_hour = self.env.ref("uom.product_uom_hour")
        attendances_by_date = self.env.context.get("attendances_by_date", [])
        project = timesheet.project_id
        attendance = get_or_default(timesheet.date, attendances_by_date)
        hours_qty = timesheet.unit_amount
        if timesheet.product_uom_id != uom_hour:
            hours_qty = timesheet.product_uom_id._compute_quantity(
                timesheet.unit_amount, uom_hour, round=False
            )
        # Get the day filled ratio
        # If attendance hours qty is empty, it is an extra work day
        days_qty = hours_qty / (
            attendance["hours_qty"] or DEFAULT_TIME_QTY["hours_qty"]
        )
        # If hours filled the day then prefer to get ratio from the conf
        # To avoid setting a full day if conf says half one only
        if days_qty == 1:
            days_qty = attendance["days_qty"]
        values = {
            "name": self._hook_get_name_from_timesheet(timesheet),
            "type": self._hook_get_type_from_timesheet(timesheet),
            "model_id": aal_model_id.id,
            "res_id": timesheet.id,
            "date": timesheet.date,
            "employee_id": timesheet.employee_id.id,
            "project_id": project.id,
            "analytic_group_id": timesheet.group_id.id,
            "hours_qty": hours_qty,
            "days_qty": days_qty,
        }
        return values

    @api.model
    def _prepare_timesheets_lines(
        self, employee, date_from=None, date_to=fields.Date().today()
    ):
        """ Retrieve all timesheets values

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        _logger.debug(f"process timesheets lines")
        if not date_from:
            date_from = employee.first_contract_date
        aal_model = self.env["account.analytic.line"]
        timesheets = aal_model.search(
            [
                ("employee_id", "=", employee.id),
                ("project_id", "!=", False),
                ("unit_amount", "!=", 0.0),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
        )
        values_list = []
        for timesheet in timesheets:
            values = self._prepare_timesheet_line(timesheet)
            if values:
                values_list.append(values)
        return values_list

    @api.model
    def _prepare_values(self, employee, date_from=None, date_to=fields.Date().today()):
        """ Return a list of dict with computed values for this employee

        :param employee: an employee record
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        if not date_from:
            date_from = employee.first_contract_date
        attendances_by_date = self.env.context.get("attendances_by_date", [])
        timesheet_values = self._prepare_timesheets_lines(employee, date_from, date_to)
        return list(attendances_by_date.values()) + timesheet_values

    @api.model
    def create_or_update(self, values):
        """ This method aims to allow proper creation or update of a line """
        to_create = []
        for value in values:
            existing_line = self.search(
                [
                    (field, "=", value.get(field, False))
                    for field in get_valid_search_fields()
                ]
            )
            if existing_line:
                # We only update if the line has been flagged as so
                if existing_line.is_invalidated:
                    value["is_invalidated"] = False
                    existing_line.write(value)
            else:
                to_create.append(value)
        if to_create:
            self.create(to_create)

    @api.model
    def action_generate_data(
        self,
        employee_ids=None,
        date_from=None,
        date_to=fields.Date().today(),
        force=False,
    ):
        """ Launch update process
        In case of force update, we unlink all related lines and reprocess them
        completely

        :param employee_ids: a list of employee ids
        :param date_from: a datetime.date object (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        :param force: purge all lines related to params before regenerating
        """
        employees = self.env["hr.employee"].browse(employee_ids)
        if not employees:
            employees = self.env["hr.employee"].search([])

        for index, employee in enumerate(employees):
            if not date_from:
                date_from = employee.first_contract_date
            # Generation can be very long and memory could be overhelmed
            # A new cursor with a commit at the end of each employee avoid that
            with registry(self.env.cr.dbname).cursor() as emp_cr:
                context = self.with_context(active_test=False).env.context
                emp_env = api.Environment(emp_cr, self.env.uid, context)
                self_env = self.with_env(emp_env)
                existing_lines = self_env.search(
                    [
                        ("employee_id", "=", employee.id),
                        ("date", ">=", date_from),
                        ("date", "<=", date_to),
                    ]
                )
                if existing_lines and force:
                    _logger.info(
                        f"Purge hours for '{employee.name}' from {date_from} to {date_to}"
                    )
                    existing_lines.unlink()
                _logger.info(
                    f"Generating hours for '{employee.name}' from {date_from} to {date_to}"
                )
                attendances_by_date = self_env._get_attendances_values_by_date(
                    employee, date_from, date_to
                )
                values = self_env.with_context(
                    attendances_by_date=attendances_by_date, active_test=False
                )._prepare_values(employee, date_from, date_to)
                self_env.create_or_update(values)
                emp_cr.commit()
