# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 - 2015 Savoir-faire Linux. All Rights Reserved.
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


class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'

    def timesheet_mapping(
        self, cr, uid,
        timesheets, payslip,
        date_from, date_to, date_format,
        context=None,
    ):
        if not payslip.contract_id:
            raise orm.except_orm(
                _("Error"),
                _("You have not defined a contract for the payslip %s")
                % payslip.name)

        contract = payslip.contract_id

        # map timesheets by date because each date may have a
        # different hourly rate
        worked_days = {}
        for ts in timesheets:
            for act in ts.timesheet_ids:
                if date_from <= act.date <= date_to:
                    act_id = act.activity_id.id
                    wd = (ts.id, act_id, act.date)
                    if wd in worked_days:
                        worked_days[wd]['number_of_hours'] \
                            += act.unit_amount
                    else:
                        worked_days[wd] = {
                            'date': act.date,
                            'number_of_hours': act.unit_amount,
                        }

        if contract.salary_computation_method == 'hourly_rate':
            # get dict of hourly rates to use for mapping
            rates_dict = {
                j.job_id.id: [
                    r for r in j.hourly_rate_class_id.line_ids
                    if r.date_start <= date_to
                    and (not r.date_end or r.date_end >= date_from)
                ]
                for j in contract.contract_job_ids
                if j.hourly_rate_class_id
            }

        res = {}

        # map timesheets by rate
        for (ts_id, ts_act, ts_date) in worked_days:
            wd = worked_days[(ts_id, ts_act, ts_date)]

            activity = self.pool['hr.activity'].browse(
                cr, uid, ts_act, context=context
            )

            ts_rate = False

            # Case employee is paid by hourly rates
            if contract.salary_computation_method == 'hourly_rate':
                # Case activity is a job
                if(
                    activity.type == 'job' and
                    activity.job_id.id in rates_dict
                ):
                    rates = rates_dict[activity.job_id.id]
                    for r in rates:
                        if(
                            r.date_start <= ts_date
                            and (not r.date_end or ts_date <= r.date_end)
                        ):
                            ts_rate = r.rate
                            break

                # Case activity is not a job position (example: a leave type)
                elif activity.type != 'job' and \
                        (
                            activity.type != 'leave'
                            or activity.leave_id.paid_leave
                        ):
                    ts_rate = self.pool['hr.contract'].get_job_hourly_rate(
                        cr, uid, date_from=ts_date, date_to=ts_date,
                        contract_id=contract.id, main_job=True, context=context
                    )

            ts = (ts_id, ts_act, ts_rate, ts_date)

            if ts in res:
                res[ts]['number_of_hours'] \
                    += wd['number_of_hours']
            else:
                res[ts] = {
                    'name': _('Timesheet'),
                    'date_from': wd['date'],
                    'date_to': wd['date'],
                    'number_of_hours': wd['number_of_hours'],
                    'contract_id': contract.id,
                    'code': 'TS',
                    'imported_from_timesheet': True,
                    'activity_id': ts_act,
                    'hourly_rate': ts_rate
                }

        return res
