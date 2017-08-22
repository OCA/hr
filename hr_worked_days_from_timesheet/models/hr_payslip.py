# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def _timesheet_mapping(self, timesheet_sheets, payslip, date_from,
                           date_to):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        # Create one worked days record for each timesheet sheet
        for ts_sheet in timesheet_sheets:
            # Get formated date from the timesheet sheet
            date_from_formated = fields.Date.to_string(
                fields.Datetime.from_string(ts_sheet.date_from))
            number_of_hours = 0
            for ts in ts_sheet.timesheet_ids:
                if date_from <= ts.date <= date_to:
                    number_of_hours += ts.unit_amount
            if number_of_hours > 0:
                self.env['hr.payslip.worked_days'].create({
                    'name': _('Timesheet %s') % date_from_formated,
                    'number_of_hours': number_of_hours,
                    'contract_id': payslip.contract_id.id,
                    'code': 'TS',
                    'imported_from_timesheet': True,
                    'timesheet_sheet_id': ts_sheet.id,
                    'payslip_id': payslip.id,
                })

    @api.multi
    def _check_contract(self):
        """Contract is not required field for payslips, yet it is for
        payslips.worked_days."""
        for payslip in self:
            if not payslip.contract_id:
                raise UserError(
                    _("Contract is not defined for one or more payslips."),
                )

    @api.multi
    def import_worked_days(self):
        """This method retreives the employee's timesheets for a payslip period
        and creates worked days records from the imported timesheets
        """
        self._check_contract()
        for payslip in self:
            date_from = payslip.date_from
            date_to = payslip.date_to

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            self.env['hr.payslip.worked_days'].search(
                [('payslip_id', '=', payslip.id),
                 ('imported_from_timesheet', '=', True)]).unlink()

            # get timesheet sheets of employee
            criteria = [
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
                ('state', '=', 'done'),
                ('employee_id', '=', payslip.employee_id.id),
            ]
            ts_model = self.env['hr_timesheet_sheet.sheet']
            timesheet_sheets = ts_model.search(criteria)
            if not timesheet_sheets:
                raise UserError(
                    _("Sorry, but there is no approved Timesheets for the \
                    entire Payslip period"),
                )
            # The reason to call this method is for other modules to modify it.
            self._timesheet_mapping(timesheet_sheets, payslip,
                                    date_from, date_to)
