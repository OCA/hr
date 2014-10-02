# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Amura Consulting. All Rights Reserved.
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
from openerp.osv import orm, osv
from openerp.tools.translate import _


class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def timesheet_mapping(self, timesheets, payslip, date_from, date_to):
        worked_days = {}
        for ts in timesheets:
            worked_days[ts.id] = {
                'name': _('Timesheet ') + ' ' + ts.date_from,
                'number_of_hours': 0,
                'contract_id': payslip.contract_id.id,
                'code': 'TS',
                'imported_from_timesheet': True,
            }
            for act in ts.timesheet_ids:
                if date_from <= act.date <= date_to:
                    worked_days[ts.id][
                        'number_of_hours'
                    ] += act.unit_amount
        return worked_days

    def import_worked_days(self, cr, uid, payslip_id, context=None):
        payslip = self.browse(cr, uid, payslip_id)[0]
        employee = payslip.employee_id

        date_from = payslip.date_from
        date_to = payslip.date_to

        # delete old imported worked_days
        old_worked_days_ids = [
            wd.id for wd in payslip.worked_days_line_ids
            if wd.imported_from_timesheet
        ]
        self.pool.get(
            'hr.payslip.worked_days'
        ).unlink(cr, uid, old_worked_days_ids, context)

        # get timesheet of employee and filter for the time interval
        timesheets = [
            ts for ts in employee.timesheet_sheet_ids
            if (
                date_from <= ts.date_from <= date_to or
                date_from <= ts.date_to <= date_to
            )
            and ts.state == 'done'
        ]
        if not timesheets:
            raise osv.except_osv(
                _("Warning"),
                _("""\
Sorry, but there is no approved Timesheets for the entire Payslip period"""),
            )

        worked_days = self.timesheet_mapping(
            timesheets,
            payslip,
            date_from,
            date_to
        )
        worked_days = [(0, 0, wd) for key, wd in worked_days.items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_days},
            context=context
        )
