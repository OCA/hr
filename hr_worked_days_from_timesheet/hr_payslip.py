# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
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
from openerp.osv import orm
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def timesheet_mapping(
        self, cr, uid,
        timesheet_sheets,
        payslip,
        date_from,
        date_to,
        date_format,
        context=None,
    ):
        """
        Take timesheet objects imported from the timesheet
        module and create a dict of worked days to be created in the payslip.
        """
        worked_days = {}
        # Create one worked days record for each timesheet sheet
        for ts_sheet in timesheet_sheets:
            # Get formated date from the timesheet sheet
            date_from = datetime.strptime(
                ts_sheet.date_from,
                DEFAULT_SERVER_DATE_FORMAT
            ).strftime(date_format)
            # Create a worked days record with no time
            worked_days[ts_sheet.id] = {
                'name': _('Timesheet %s') % date_from,
                'number_of_hours': 0,
                'contract_id': payslip.contract_id.id,
                'code': 'TS',
                'imported_from_timesheet': True,
            }
            for ts in ts_sheet.timesheet_ids:
                # The timesheet_sheet overlaps the payslip period,
                # but this does not mean that every timesheet in it
                # overlaps the payslip period.
                if date_from <= ts.date <= date_to:
                    worked_days[ts_sheet.id][
                        'number_of_hours'
                    ] += ts.unit_amount
        return worked_days

    def import_worked_days(
        self, cr, uid,
        payslip_ids,
        context=None
    ):
        """
        Retreive the employee's timesheets for a payslip period
        and create worked days records from the imported timesheets
        """
        # get user date format
        lang_pool = self.pool['res.lang']
        user_pool = self.pool['res.users']
        code = user_pool.context_get(cr, uid).get('lang', 'en_US')

        lang_id = lang_pool.search(
            cr, uid, [('code', '=', code)], context=context)

        date_format = lang_pool.read(
            cr, uid, lang_id, ['date_format'],
            context=context)[0]['date_format']

        for payslip in self.browse(cr, uid, payslip_ids, context=context):
            employee = payslip.employee_id

            date_from = payslip.date_from
            date_to = payslip.date_to

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            old_worked_days_ids = [
                wd.id for wd in payslip.worked_days_line_ids
                # We only remove records that were imported from
                # timesheets and not those manually entered.
                if wd.imported_from_timesheet
            ]
            self.pool.get(
                'hr.payslip.worked_days'
            ).unlink(cr, uid, old_worked_days_ids, context)

            # get timesheet sheets of employee
            timesheet_sheets = self.get_timesheets_from_employee(
                cr, uid,
                employee.id,
                date_from, date_to,
                context=context
            )

            # The reason to call this method is for other modules to modify it.
            worked_days = self.timesheet_mapping(
                cr, uid,
                timesheet_sheets,
                payslip,
                date_from,
                date_to,
                date_format,
                context=context,
            )
            worked_days = [(0, 0, wd) for key, wd in worked_days.items()]

            self.write(
                cr, uid, payslip.id,
                {'worked_days_line_ids': worked_days},
                context=context
            )

    def get_timesheets_from_employee(
        self, cr, uid,
        employee_id,
        date_from, date_to,
        context=None
    ):
        """
        Get timesheet sheets of an employee for a period of time
        """
        employee = self.pool['hr.employee'].browse(
            cr, uid, employee_id, context=context)

        timesheet_sheets = [
            ts_sheet for ts_sheet in employee.timesheet_sheet_ids
            if (
                # We need only the timesheet sheets that overlap
                # the payslip period.
                date_from <= ts_sheet.date_from <= date_to or
                date_from <= ts_sheet.date_to <= date_to

                # We want only approved timesheets
            ) and ts_sheet.state == 'done'
        ]

        if not timesheet_sheets:
            raise orm.except_orm(
                _("Warning"),
                _(
                    "Sorry, but there is no approved Timesheets "
                    "for the entire payslip period "
                    "for employee %s."
                ) % employee.name_get(context=context)[0][1],
            )

        return timesheet_sheets
