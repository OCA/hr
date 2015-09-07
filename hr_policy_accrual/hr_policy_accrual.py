# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
#

from datetime import datetime, date, timedelta
import logging

from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT

_l = logging.getLogger(__name__)


class hr_accrual_job(orm.Model):

    _name = 'hr.policy.line.accrual.job'
    _description = 'Accrual Policy Line Job Run'

    _columns = {
        'name': fields.date('Date', required=True, readonly=True),
        'exec': fields.datetime(
            'Execution Date/Time', required=True, readonly=True),
        'policy_line_id': fields.many2one(
            'hr.policy.line.accrual', 'Accrual Policy Line',
            required=True, readonly=True),
        'accrual_line_ids': fields.many2many(
            'hr.accrual.line', 'hr_policy_job_accrual_line_rel',
            'job_id', 'accrual_line_id', 'Accrual Lines',
            readonly=True),
        'holiday_ids': fields.many2many(
            'hr.holidays', 'hr_policy_job_holiday_rel', 'job_id',
            'holiday_id', 'Leave Allocation Requests', readonly=True),
    }


class hr_policy(orm.Model):

    _name = 'hr.policy.accrual'
    _description = 'Accrual Policy'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Effective Date', required=True),
        'line_ids': fields.one2many(
            'hr.policy.line.accrual', 'policy_id', 'Policy Lines'),
    }

    # Return records with latest date first
    _order = 'date desc'

    def get_latest_policy(self, cr, uid, policy_group, dToday, context=None):
        """Return an accrual policy with an effective date before dToday
        but greater than all the others"""

        if not policy_group or not policy_group.accr_policy_ids or not dToday:
            return None

        res = None
        for policy in policy_group.accr_policy_ids:
            dPolicy = datetime.strptime(policy.date, OE_DATEFORMAT).date()
            if dPolicy <= dToday:
                if res is None:
                    res = policy
                elif dPolicy > datetime.strptime(
                    res.date, OE_DATEFORMAT
                ).date():
                    res = policy

        return res

    def _calculate_and_deposit(
        self, cr, uid, line, employee, job_id, dToday=None, context=None
    ):

        leave_obj = self.pool.get('hr.holidays')
        accrual_obj = self.pool.get('hr.accrual')
        accrual_line_obj = self.pool.get('hr.accrual.line')
        job_obj = self.pool.get('hr.policy.line.accrual.job')
        month_last_day = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31,
        }

        srvc_months, dHire = self.pool.get(
            'hr.employee').get_months_service_to_date(
                cr, uid, [employee.id], dToday=dToday,
                context=context)[employee.id]
        srvc_months = int(srvc_months)
        if dToday is None:
            dToday = date.today()

        if line.type != 'calendar':
            return

        employed_days = 0
        dCount = dHire
        while dCount < dToday:
            employed_days += 1
            dCount += timedelta(days=+1)
        if line.minimum_employed_days > employed_days:
            return

        if line.frequency_on_hire_date:
            freq_week_day = dHire.weekday()
            freq_month_day = dHire.day
            freq_annual_month = dHire.month
            freq_annual_day = dHire.day
        else:
            freq_week_day = line.frequency_week_day
            freq_month_day = line.frequency_month_day
            freq_annual_month = line.frequency_annual_month
            freq_annual_day = line.frequency_annual_day

        premium_amount = 0
        if line.calculation_frequency == 'weekly':
            if dToday.weekday() != freq_week_day:
                return
            freq_amount = float(line.accrual_rate) / 52.0
            if line.accrual_rate_premium_minimum <= srvc_months:
                premium_amount = (
                    max(
                        0, srvc_months - line.accrual_rate_premium_minimum +
                        line.accrual_rate_premium_milestone
                    )
                ) // (
                    line.accrual_rate_premium_milestone *
                    line.accrual_rate_premium
                ) / 52.0
        elif line.calculation_frequency == 'monthly':
            # When deciding to skip an employee account for actual month
            # lengths. If the frequency date is 31 and this month only has 30
            # days, go ahead and do the accrual on the last day of the month
            # (i.e. the 30th). For February, on non-leap years execute accruals
            # for the 29th on the 28th.
            #
            if dToday.day == month_last_day[
                dToday.month
            ] and freq_month_day > dToday.day:
                if dToday.month != 2:
                    freq_month_day = dToday.day
                elif dToday.month == 2 and dToday.day == 28 and (
                    dToday + timedelta(days=+1)
                ).day != 29:
                    freq_month_day = dToday.day

            if dToday.day != freq_month_day:
                return

            freq_amount = float(line.accrual_rate) / 12.0
            if line.accrual_rate_premium_minimum <= srvc_months:
                premium_amount = (
                    max(
                        0, srvc_months - line.accrual_rate_premium_minimum +
                        line.accrual_rate_premium_milestone
                    )
                ) // (
                    line.accrual_rate_premium_milestone *
                    line.accrual_rate_premium
                ) / 12.0
        else:  # annual frequency
            # On non-leap years execute Feb. 29 accruals on the 28th
            #
            if (
                dToday.month == 2 and
                dToday.day == 28 and
                (
                    dToday + timedelta(days=+1)
                ).day != 29 and
                freq_annual_day > dToday.day
            ):
                freq_annual_day = dToday.day

            if (
                dToday.month != freq_annual_month and
                dToday.day != freq_annual_day
            ):
                return

            freq_amount = line.accrual_rate
            if line.accrual_rate_premium_minimum <= srvc_months:
                premium_amount = (
                    max(
                        0, srvc_months - line.accrual_rate_premium_minimum +
                        line.accrual_rate_premium_milestone
                    )
                ) // (
                    line.accrual_rate_premium_milestone *
                    line.accrual_rate_premium)

        if line.accrual_rate_max == 0:
            amount = freq_amount + premium_amount
        else:
            amount = min(freq_amount + premium_amount, line.accrual_rate_max)

        # Deposit to the accrual account
        #
        accrual_line = {
            'date': dToday.strftime(OE_DATEFORMAT),
            'accrual_id': line.accrual_id.id,
            'employee_id': employee.id,
            'amount': amount,
        }
        acr_id = accrual_line_obj.create(
            cr, uid, accrual_line, context=context)
        accrual_obj.write(
            cr, uid, line.accrual_id.id, {'line_ids': [(4, acr_id)]})

        # Add the leave and trigger validation workflow
        #
        leave_allocation = {
            'name': 'Calendar based accrual (' + line.name + ')',
            'type': 'add',
            'employee_id': employee.id,
            'number_of_days_temp': amount,
            'holiday_status_id': line.accrual_id.holiday_status_id.id,
            'from_accrual': True,
        }
        holiday_id = leave_obj.create(
            cr, uid, leave_allocation, context=context)
        netsvc.LocalService('workflow').trg_validate(
            uid, 'hr.holidays', holiday_id, 'validate', cr)

        # Add this accrual line and holiday request to the job for this
        # policy line
        #
        job_obj.write(
            cr, uid, job_id, {'accrual_line_ids': [
                (4, acr_id)], 'holiday_ids': [(4, holiday_id)]},
            context=context)

    def _get_last_calculation_date(self, cr, uid, accrual_id, context=None):

        job_obj = self.pool.get('hr.policy.line.accrual.job')

        job_ids = job_obj.search(cr, uid, [
            ('policy_line_id', '=', accrual_id),
        ],
            order='name desc', limit=1, context=context)
        if len(job_ids) == 0:
            return None

        data = job_obj.read(cr, uid, job_ids[0], ['name'], context=context)
        return datetime.strptime(data['name'], OE_DATEFORMAT).date()

    def try_calculate_accruals(self, cr, uid, context=None):

        pg_obj = self.pool.get('hr.policy.group')
        job_obj = self.pool.get('hr.policy.line.accrual.job')
        dToday = datetime.now().date()

        pg_ids = pg_obj.search(cr, uid, [], context=context)
        for pg in pg_obj.browse(cr, uid, pg_ids, context=context):
            accrual_policy = self.get_latest_policy(
                cr, uid, pg, dToday, context=context)
            if accrual_policy is None:
                continue

            # Get the last time that an accrual job was run for each accrual
            # line in the accrual policy. If there was no 'last time' assume
            # this is the first time the job is being run and start it running
            # from today.
            #
            line_jobs = {}
            for line in accrual_policy.line_ids:
                d = self._get_last_calculation_date(
                    cr, uid, line.id, context=context)
                if d is None:
                    line_jobs[line.id] = [dToday]
                else:
                    line_jobs[line.id] = []
                    while d < dToday:
                        d += timedelta(days=1)
                        line_jobs[line.id].append(d)

            # For each accrual line in this accrual policy do a run for each
            # day (beginning
            # from the last date for which it was run) until today for each
            # contract attached to the policy group.
            #
            for line in accrual_policy.line_ids:
                for dJob in line_jobs[line.id]:

                    # Create a Job for the accrual line
                    job_vals = {
                        'name': dJob.strftime(OE_DATEFORMAT),
                        'exec': datetime.now().strftime(OE_DATETIMEFORMAT),
                        'policy_line_id': line.id,
                    }
                    job_id = job_obj.create(cr, uid, job_vals, context=context)

                    employee_list = []
                    for contract in pg.contract_ids:
                        if (
                            contract.employee_id.id in employee_list or
                            contract.state in ['draft', 'done']
                        ):
                            continue
                        if (
                            contract.date_end and
                            datetime.strptime(
                                contract.date_end, OE_DATEFORMAT).date() < dJob
                        ):
                            continue
                        self._calculate_and_deposit(
                            cr, uid, line, contract.employee_id,
                            job_id, dToday=dJob, context=context)

                        # An employee may have multiple valid contracts. Don't
                        # double-count.
                        employee_list.append(contract.employee_id.id)

        return True


class hr_policy_line(orm.Model):

    _name = 'hr.policy.line.accrual'
    _description = 'Accrual Policy Line'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
        'policy_id': fields.many2one('hr.policy.accrual', 'Accrual Policy'),
        'accrual_id': fields.many2one(
            'hr.accrual', 'Accrual Account', required=True),
        'type': fields.selection([
            ('standard', 'Standard'), ('calendar', 'Calendar')
        ], 'Type', required=True),
        'balance_on_payslip': fields.boolean(
            'Display Balance on Pay Slip',
            help='The pay slip report must be modified to display this accrual'
                 ' for this setting to have any effect.'
        ),
        'calculation_frequency': fields.selection([
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('annual', 'Annual'),
        ],
            'Calculation Frequency', required=True),
        'frequency_on_hire_date': fields.boolean(
            'Frequency Based on Hire Date'),
        'frequency_week_day': fields.selection([('0', 'Monday'),
                                                ('1', 'Tuesday'),
                                                ('2', 'Wednesday'),
                                                ('3', 'Thursday'),
                                                ('4', 'Friday'),
                                                ('5', 'Saturday'),
                                                ('6', 'Sunday'),
                                                ],
                                               'Week Day'),
        'frequency_month_day': fields.selection([
            ('1', '1'), ('2', '2'), ('3', '3'), (
                '4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
            ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), (
                '12', '12'), ('13', '13'), ('14', '14'),
            ('15', '15'), ('16', '16'), ('17', '17'), (
                '18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
            ('22', '22'), ('23', '23'), ('24', '24'), (
                '25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),
            ('29', '29'), ('30', '30'), ('31', '31'),
        ],
            'Day of Month'),
        'frequency_annual_month': fields.selection([
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ], 'Month'),
        'frequency_annual_day': fields.selection([
            ('1', '1'), ('2', '2'), ('3', '3'), (
                '4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
            ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), (
                '12', '12'), ('13', '13'), ('14', '14'),
            ('15', '15'), ('16', '16'), ('17', '17'), (
                '18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
            ('22', '22'), ('23', '23'), ('24', '24'), (
                '25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),
            ('29', '29'), ('30', '30'), ('31', '31'),
        ],
            'Day of Month'),
        'minimum_employed_days': fields.integer('Minimum Employed Days'),
        'accrual_rate': fields.float(
            'Accrual Rate', required=True,
            help='The rate, in days, accrued per year.'),
        'accrual_rate_premium': fields.float(
            'Accrual Rate Premium', required=True,
            help='The additional amount of time (beyond the standard rate) '
                 'accrued per Premium Milestone of service.'
        ),
        'accrual_rate_premium_minimum': fields.integer(
            'Months of Employment Before Premium', required=True,
            help="Minimum number of months the employee must be employed "
                 "before the premium rate will start to accrue."
        ),
        'accrual_rate_premium_milestone': fields.integer(
            'Accrual Premium Milestone', required=True,
            help="Number of milestone months after which the premium rate will"
                 " be added."
        ),
        'accrual_rate_max': fields.float(
            'Maximum Accrual Rate', required=True,
            help='The maximum amount of time that may accrue per year. '
                 'Zero means the amount may keep increasing indefinitely.'
        ),
        'job_ids': fields.one2many(
            'hr.policy.line.accrual.job', 'policy_line_id', 'Jobs',
            readonly=True),
    }

    _defaults = {
        'type': 'calendar',
        'minimum_employed_days': 0,
        'accrual_rate_max': 0.0,
        'accrual_rate_premium_minimum': 12,
    }


class policy_group(orm.Model):

    _name = 'hr.policy.group'
    _inherit = 'hr.policy.group'

    _columns = {
        'accr_policy_ids': fields.many2many(
            'hr.policy.accrual', 'hr_policy_group_accr_rel',
            'group_id', 'accr_id', 'Accrual Policy'),
    }


class hr_holidays(orm.Model):

    _name = 'hr.holidays'
    _inherit = 'hr.holidays'

    _columns = {
        'from_accrual': fields.boolean(
            'Created by Accrual Policy Line',
            help='Used to differentiate allocations from accruals and manual '
                 'allocations',
            readonly=True),
    }

    def _do_accrual(
        self, cr, uid, today, holiday_status_id, employee_id, days,
        context=None
    ):

        accrual_obj = self.pool.get('hr.accrual')
        accrual_line_obj = self.pool.get('hr.accrual.line')

        accrual_ids = accrual_obj.search(
            cr, uid, [('holiday_status_id', '=', holiday_status_id)],
            context=context)

        if len(accrual_ids) == 0:
            return

        # Deposit to the accrual account
        #
        accrual_line = {
            'date': today,
            'accrual_id': accrual_ids[0],
            'employee_id': employee_id,
            'amount': days,
        }
        line_id = accrual_line_obj.create(
            cr, uid, accrual_line, context=context)
        accrual_obj.write(
            cr, uid, accrual_ids[0], {'line_ids': [(4, line_id)]})

        return

    def holidays_validate(self, cr, uid, ids, context=None):

        res = super(hr_holidays, self).holidays_validate(
            cr, uid, ids, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        today = datetime.now().strftime(OE_DATEFORMAT)
        for record in self.browse(cr, uid, ids, context=context):
            if (
                record.holiday_type == 'employee' and
                record.type == 'add' and not record.from_accrual
            ):

                self._do_accrual(
                    cr, uid, today, record.holiday_status_id.id,
                    record.employee_id.id,
                    record.number_of_days_temp, context=context)

            elif record.holiday_type == 'employee' and record.type == 'remove':

                self._do_accrual(
                    cr, uid, today, record.holiday_status_id.id,
                    record.employee_id.id,
                    -record.number_of_days_temp, context=context)

        return res

    def holidays_refuse(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        today = datetime.now().strftime(OE_DATEFORMAT)
        for record in self.browse(cr, uid, ids, context=context):
            if record.state not in ['validate', 'validate1']:
                continue

            if record.holiday_type == 'employee' and record.type == 'add':

                self._do_accrual(
                    cr, uid, today, record.holiday_status_id.id,
                    record.employee_id.id,
                    -record.number_of_days_temp, context=context)

            elif record.holiday_type == 'employee' and record.type == 'remove':

                self._do_accrual(
                    cr, uid, today, record.holiday_status_id.id,
                    record.employee_id.id,
                    record.number_of_days_temp, context=context)
        return super(hr_holidays, self).holidays_refuse(
            cr, uid, ids, context=None)
