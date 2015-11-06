# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
#    Copyright (C) 2015 Acysos S.L. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def timesheet_mapping(self, timesheet_sheets, payslip, date_from, date_to,
                          date_format):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        # Create one worked days record for each timesheet sheet
        wd_model = self.env['hr.payslip.worked_days']
        for ts_sheet in timesheet_sheets:
            # Get formated date from the timesheet sheet
            date_from_formated = datetime.strptime(
                ts_sheet.date_from,
                DEFAULT_SERVER_DATE_FORMAT
            ).strftime(date_format)

            number_of_hours = 0
            for ts in ts_sheet.timesheet_ids:
                if date_from <= ts.date <= date_to:
                    number_of_hours += ts.unit_amount

            if number_of_hours > 0:
                wd_model.create({
                    'name': _('Timesheet %s') % date_from_formated,
                    'number_of_hours': number_of_hours,
                    'contract_id': payslip.contract_id.id,
                    'code': 'TS',
                    'imported_from_timesheet': True,
                    'timesheet_sheet_id': ts_sheet.id,
                    'payslip_id': payslip.id,
                })

    @api.multi
    def import_worked_days(self):
        """This method retreives the employee's timesheets for a payslip period
        and creates worked days records from the imported timesheets
        """
        for payslip in self:

            date_from = payslip.date_from
            date_to = payslip.date_to

            # get user date format
            date_format = self.env['res.lang'].search(
                [('code', '=', self.env.user.lang)]).date_format

            if not date_format:
                date_format = '%m/%d/%Y'

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            wd_model = self.env['hr.payslip.worked_days']
            wd_model.search(
                [('payslip_id', '=', payslip.id),
                 ('imported_from_timesheet', '=', True)]).unlink()

            # get timesheet sheets of employee
            timesheet_sheets = self.env['hr_timesheet_sheet.sheet'].search(
                ['&', '&', '|', '&',
                 ('date_from', '<=', date_to), ('date_from', '>=', date_from),
                 '&', ('date_to', '<=', date_to), ('date_to', '>=', date_from),
                 ('state', '=', 'done'),
                 ('employee_id', '=', payslip.employee_id.id)]
            )

            if not timesheet_sheets:
                raise Exception(
                    _("Warning"),
                    _("Sorry, but there is no approved Timesheets for the \
                    entire Payslip period"),
                )

            # The reason to call this method is for other modules to modify it.
            self.timesheet_mapping(
                timesheet_sheets,
                payslip,
                date_from,
                date_to,
                date_format,
            )
