# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.model
    def prepare_worked_days(self, payslip, ts_sheet, date_from, date_to):
        number_of_hours = 0
        for ts in ts_sheet.timesheet_ids:
            if date_from <= ts.date <= date_to:
                number_of_hours += ts.unit_amount
        # Get formatted date from the timesheet sheet
        date_from_formatted = ts_sheet.date_start
        number_of_days = (date_to - date_from).days
        if number_of_hours > 0 and number_of_days > 0:
            return {
                "name": _("Timesheet %s") % date_from_formatted,
                "number_of_hours": number_of_hours,
                "number_of_days": number_of_days,
                "contract_id": payslip.contract_id.id,
                "code": "TS",
                "imported_from_timesheet": True,
                "timesheet_sheet_id": ts_sheet.id,
                "payslip_id": payslip.id,
            }
        return False

    def _timesheet_mapping(self, timesheet_sheets, payslip, date_from, date_to):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        # Create one worked days record for each timesheet sheet
        for ts_sheet in timesheet_sheets:
            worked_days_data = self.prepare_worked_days(
                payslip, ts_sheet, date_from, date_to
            )
            if worked_days_data:
                self.env["hr.payslip.worked_days"].create(worked_days_data)

    def _check_contract(self):
        """Contract is not required field for payslips, yet it is for
        payslips.worked_days."""
        for payslip in self:
            if not payslip.contract_id:
                raise UserError(
                    _("Contract is not defined for one or more payslips."),
                )

    @api.model
    def get_timesheets_from_employee(self, employee, date_from, date_to):
        criteria = [
            ("date_start", ">=", date_from),
            ("date_end", "<=", date_to),
            ("state", "=", "done"),
            ("employee_id", "=", employee.id),
        ]
        ts_model = self.env["hr_timesheet.sheet"]
        timesheet_sheets = ts_model.search(criteria)
        if not timesheet_sheets:
            raise UserError(
                _(
                    "Sorry, but there is no approved Timesheets for "
                    "the entire Payslip period for user {}"
                ).format(employee.name)
            )
        return timesheet_sheets

    def import_worked_days(self):
        """This method retrieves the employee's timesheet for a payslip period
        and creates worked days records from the imported timesheet
        """
        self._check_contract()
        for payslip in self:
            date_from = payslip.date_from
            date_to = payslip.date_to

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            self.env["hr.payslip.worked_days"].search(
                [
                    ("payslip_id", "=", payslip.id),
                    ("imported_from_timesheet", "=", True),
                ]
            ).unlink()

            # get timesheet sheets of employee
            timesheet_sheets = self.get_timesheets_from_employee(
                payslip.employee_id, date_from, date_to
            )
            # The reason to call this method is for other modules to modify it.
            self._timesheet_mapping(timesheet_sheets, payslip, date_from, date_to)
