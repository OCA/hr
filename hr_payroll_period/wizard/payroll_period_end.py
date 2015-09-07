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

import logging
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OEDATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OEDATE_FORMAT
from openerp.tools.translate import _
from openerp.osv import fields, orm


_logger = logging.getLogger(__name__)


class payroll_period_end_1(orm.TransientModel):

    _name = 'hr.payroll.period.end.1'
    _description = 'End of Payroll Period Wizard Step 1'

    _change_res = {
        'br100': 0,
        'br50': 0,
        'br10': 0,
        'br5': 0,
        'br1': 0,
        'cent50': 0,
        'cent25': 0,
        'cent10': 0,
        'cent05': 0,
        'cent01': 0,
        'done': False,
    }

    _columns = {
        'period_id': fields.integer(
            'Period ID',
        ),
        'is_ended': fields.boolean(
            'Past End Day?',
        ),
        'public_holiday_ids': fields.many2many(
            'hr.holidays.public.line',
            'hr_holidays_pay_period_rel',
            'holiday_id',
            'period_id',
            'Public Holidays',
            readonly=True,
        ),
        'alert_critical': fields.integer(
            'Critical Severity',
            readonly=True,
        ),
        'alert_high': fields.integer(
            'High Severity',
            readonly=True,
        ),
        'alert_medium': fields.integer(
            'Medium Severity',
            readonly=True,
        ),
        'alert_low': fields.integer(
            'Low Severity',
            readonly=True
        ),
        'pex_critical': fields.integer(
            'Critical',
            readonly=True,
        ),
        'pex_high': fields.integer(
            'High',
            readonly=True,
        ),
        'pex_medium': fields.integer(
            'Medium',
            readonly=True,
        ),
        'pex_low': fields.integer(
            'Low',
            readonly=True,
        ),
        'locked': fields.boolean(
            'Is Period Locked?',
            readonly=True,
        ),
        'can_unlock': fields.boolean(
            'Can Unlock Period?',
            readonly=True,
        ),
        'payslips': fields.boolean(
            'Have Pay Slips Been Generated?',
            readonly=True,
        ),
        'ps_generated': fields.boolean(
            'Pay Slip Generated?',
            readonly=True,
        ),
        'payment_started': fields.boolean(
            'Payment Started?',
            readonly=True,
        ),
        'closed': fields.boolean(
            'Pay Period Closed?',
            readonly=True,
        ),
        'br100': fields.integer(
            '100 Birr',
            readonly=True,
        ),
        'br50': fields.integer(
            '50 Birr',
            readonly=True,
        ),
        'br10': fields.integer(
            '10 Birr',
            readonly=True,
        ),
        'br5': fields.integer(
            '5 Birr',
            readonly=True,
        ),
        'br1': fields.integer(
            '1 Birr',
            readonly=True,
        ),
        'cent50': fields.integer(
            '50 Cents',
            readonly=True,
        ),
        'cent25': fields.integer(
            '25 Cents',
            readonly=True,
        ),
        'cent10': fields.integer(
            '10 Cents',
            readonly=True,
        ),
        'cent05': fields.integer(
            '5 Cents',
            readonly=True,
        ),
        'cent01': fields.integer(
            '1 Cent',
            readonly=True,
        ),
        'exact_change': fields.char(
            'Exact Change Total',
            size=32,
            readonly=True,
        ),
        'ps_amendments_conf': fields.many2many(
            'hr.payslip.amendment',
            'hr_payslip_pay_period_rel',
            'amendment_id',
            'period_id',
            'Confirmed Amendments',
            readonly=True,
        ),
        'ps_amendments_draft': fields.many2many(
            'hr.payslip.amendment',
            'hr_payslip_pay_period_rel',
            'amendment_id',
            'period_id',
            'Draft Amendments',
            readonly=True,
        ),
    }

    def _get_period_id(self, cr, uid, context=None):

        if context is None:
            context = {}
        return context.get('active_id', False)

    def _get_is_ended(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            flag = self.pool.get('hr.payroll.period').is_ended(
                cr, uid, period_id, context=context)
        return flag

    def _alerts_count(self, cr, uid, severity, context=None):

        alert_obj = self.pool.get('hr.schedule.alert')

        if context is None:
            context = {}
        period_id = context.get('active_id', False)

        alert_ids = []
        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period:
                employee_ids = []
                [employee_ids.append(c.employee_id.id)
                 for c in period.schedule_id.contract_ids]
                alert_ids = alert_obj.search(
                    cr, uid, ['&', ('name', '>=', period.date_start),
                              ('name', '<=', period.date_end),
                              ('severity', '=', severity),
                              ('employee_id', 'in', employee_ids),
                              ],
                    context=context)
        return len(alert_ids)

    def _critical_alerts(self, cr, uid, context=None):
        return self._alerts_count(cr, uid, 'critical', context)

    def _high_alerts(self, cr, uid, context=None):
        return self._alerts_count(cr, uid, 'high', context)

    def _medium_alerts(self, cr, uid, context=None):
        return self._alerts_count(cr, uid, 'medium', context)

    def _low_alerts(self, cr, uid, context=None):
        return self._alerts_count(cr, uid, 'low', context)

    def _pex_count(self, cr, uid, severity, context=None):
        ex_obj = self.pool.get('hr.payslip.exception')
        run_obj = self.pool.get('hr.payslip.run')

        if context is None:
            context = {}
        period_id = context.get('active_id', False)

        ex_ids = []
        slip_ids = []
        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period and period.register_id:
                for run_id in period.register_id.run_ids:
                    data = run_obj.read(
                        cr, uid, run_id.id, ['slip_ids'], context=context)
                    [slip_ids.append(i) for i in data['slip_ids']]
                ex_ids = ex_obj.search(cr, uid, [('severity', '=', severity),
                                                 ('slip_id', 'in', slip_ids),
                                                 ],
                                       context=context)
        return len(ex_ids)

    def _pex_critical(self, cr, uid, context=None):
        return self._pex_count(cr, uid, 'critical', context)

    def _pex_high(self, cr, uid, context=None):
        return self._pex_count(cr, uid, 'high', context)

    def _pex_medium(self, cr, uid, context=None):
        return self._pex_count(cr, uid, 'medium', context)

    def _pex_low(self, cr, uid, context=None):
        return self._pex_count(cr, uid, 'low', context)

    def _no_missing_punches(self, cr, uid, context=None):
        ids = self._missing_punches(cr, uid, context)
        res = len(ids)
        return res

    def _missing_punches(self, cr, uid, context=None):

        #
        # TODO - Someone who cares about DST should update this code to handle
        #  it.
        #

        missing_punch_ids = []
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period:
                attendance_obj = self.pool.get('hr.attendance')
                utc_tz = timezone('UTC')
                dt = datetime.strptime(period.date_start, '%Y-%m-%d %H:%M:%S')
                utcDtStart = utc_tz.localize(dt, is_dst=False)
                dt = datetime.strptime(period.date_end, '%Y-%m-%d %H:%M:%S')
                utcDtEnd = utc_tz.localize(dt, is_dst=False)
                for contract in period.schedule_id.contract_ids:
                    employee = contract.employee_id
                    punch_ids = attendance_obj.search(cr, uid, [
                        ('employee_id', '=', employee.id),
                        '&',
                        ('name', '>=', utcDtStart.strftime(
                            '%Y-%m-%d %H:%M:S')),
                        ('name', '<=', utcDtEnd.strftime(
                            '%Y-%m-%d %H:%M:S')),
                    ], order='name', context=context)
                    prevPunch = False
                    if len(punch_ids) > 0:
                        punches = attendance_obj.browse(
                            cr, uid, punch_ids, context=context)
                        for punch in punches:
                            if not prevPunch:
                                # First Punch must be a sign-in
                                if punch.action != 'sign_in':
                                    missing_punch_ids.append(punch.id)
                            elif punch.action == 'sign_in':
                                if prevPunch.action != 'sign_out':
                                    missing_punch_ids.append(prevPunch.id)
                            elif punch.action == 'sign_out':
                                if prevPunch.action != 'sign_in':
                                    missing_punch_ids.append(punch.id)
                            prevPunch = punch
                        # The last punch should be a sign out
                        if prevPunch and prevPunch.action != 'sign_out':
                            missing_punch_ids.append(prevPunch.id)
        return missing_punch_ids

    def _get_locked(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state'], context=context)
            flag = (data.get('state') in [
                    'locked', 'generate', 'payment', 'closed'])

        return flag

    def _get_can_unlock(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state'], context=context)
            flag = (data.get('state') in ['locked', 'generate'])

        return flag

    def _get_payslips(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state', 'register_id'], context=context)
            flag |= (
                data.get('state') in ['generate', 'payment', 'closed'] and
                data.get('register_id', False)
            )

        return flag

    def _get_ps_generated(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state'], context=context)
            if data.get('state') in ['generate']:
                flag = True

        return flag

    def _get_payment_started(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state'], context=context)
            if data.get('state') in ['payment', 'closed']:
                flag = True

        return flag

    def _get_change(self, cr, uid, context=None):

        if self._change_res['done']:
            return self._change_res

        self._change_res = {
            'br100': 0,
            'br50': 0,
            'br10': 0,
            'br5': 0,
            'br1': 0,
            'cent50': 0,
            'cent25': 0,
            'cent10': 0,
            'cent05': 0,
            'cent01': 0,
            'done': False,
        }

        net_lines = []
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['register_id'], context=context
            )
            if data['register_id']:
                data = self.pool.get(
                    'hr.payroll.register').read(
                    cr, uid, data['register_id'][0], ['run_ids'],
                    context=context
                )
                if data['run_ids']:
                    ps_runs = self.pool.get(
                        'hr.payslip.run').browse(cr, uid, data['run_ids'],
                                                 context=context)
                    for psr in ps_runs:
                        for slip in psr.slip_ids:
                            for line in slip.line_ids:
                                if line.salary_rule_id.code == 'NET':
                                    net_lines.append(line.total)
        if len(net_lines) > 0:
            for net in net_lines:
                cents, birrs = math.modf(net)

                birrs = int(birrs)
                cents = int(round(cents, 2) * 100.0)
                if birrs >= 100:
                    self._change_res['br100'] += birrs / 100
                    birrs %= 100
                if birrs >= 50:
                    self._change_res['br50'] += birrs / 50
                    birrs %= 50
                if birrs >= 10:
                    self._change_res['br10'] += birrs / 10
                    birrs %= 10
                if birrs >= 5:
                    self._change_res['br5'] += birrs / 5
                    birrs %= 5
                if birrs >= 1:
                    self._change_res['br1'] += birrs

                if cents >= 50:
                    self._change_res['cent50'] += cents / 50
                    cents %= 50
                if cents >= 25:
                    self._change_res['cent25'] += cents / 25
                    cents %= 25
                if cents >= 10:
                    self._change_res['cent10'] += cents / 10
                    cents %= 10
                if cents >= 5:
                    self._change_res['cent05'] += cents / 5
                    cents %= 5
                if cents >= 1:
                    self._change_res['cent01'] += cents
            self._change_res['done'] = True

        return self._change_res

    def _get_br100(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['br100']

    def _get_br50(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['br50']

    def _get_br10(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['br10']

    def _get_br5(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['br5']

    def _get_br1(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['br1']

    def _get_cent50(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['cent50']

    def _get_cent25(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['cent25']

    def _get_cent10(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['cent10']

    def _get_cent05(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['cent05']

    def _get_cent01(self, cr, uid, context=None):

        return self._get_change(cr, uid, context=context)['cent01']

    def _get_change_total(self, cr, uid, context=None):

        birr = self._change_res['br100'] * 100
        birr += self._change_res['br50'] * 50
        birr += self._change_res['br10'] * 10
        birr += self._change_res['br5'] * 5
        birr += self._change_res['br1']

        cents = self._change_res['cent50'] * 50
        cents += self._change_res['cent25'] * 25
        cents += self._change_res['cent10'] * 10
        cents += self._change_res['cent05'] * 5
        cents += self._change_res['cent01']

        birr += cents / 100
        cents %= 100

        return 'Br ' + str(birr) + '.' + str(cents)

    def _get_closed(self, cr, uid, context=None):

        flag = False
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if period_id:
            data = self.pool.get('hr.payroll.period').read(
                cr, uid, period_id, ['state'], context=context)
            if data.get('state') in ['closed']:
                flag = True

        return flag

    def _get_public_holidays(self, cr, uid, context=None):

        holiday_ids = []
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return holiday_ids

        data = self.pool.get('hr.payroll.period').read(
            cr, uid, period_id, ['date_start', 'date_end'], context=context
        )
        start = datetime.strptime(
            data['date_start'], OEDATETIME_FORMAT).date().strftime(
                OEDATE_FORMAT)
        end = datetime.strptime(
            data['date_end'], OEDATETIME_FORMAT).date().strftime(OEDATE_FORMAT)
        holiday_ids = self.pool.get('hr.holidays.public.line').search(
            cr, uid, [
                '&',
                ('date', '>=', start),
                ('date', '<=', end),
            ], context=context
        )

        return holiday_ids

    def _get_confirmed_amendments(self, cr, uid, context=None):

        psa_ids = []
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return psa_ids

        psa_ids = self.pool.get(
            'hr.payslip.amendment').search(
                cr, uid, [
                    ('pay_period_id', '=', period_id),
                    ('state', 'in', ['validate']),
                ], context=context
        )
        return psa_ids

    def _get_draft_amendments(self, cr, uid, context=None):

        psa_ids = []
        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return psa_ids

        psa_ids = self.pool.get(
            'hr.payslip.amendment').search(
                cr, uid, [
                    ('pay_period_id', '=', period_id),
                    ('state', 'in', ['draft']),
                ], context=context
        )
        return psa_ids

    _defaults = {
        'period_id': _get_period_id,
        'is_ended': _get_is_ended,
        'public_holiday_ids': _get_public_holidays,
        'alert_critical': _critical_alerts,
        'alert_high': _high_alerts,
        'alert_medium': _medium_alerts,
        'alert_low': _low_alerts,
        'pex_critical': _pex_critical,
        'pex_high': _pex_high,
        'pex_medium': _pex_medium,
        'pex_low': _pex_low,
        'locked': _get_locked,
        'can_unlock': _get_can_unlock,
        'ps_generated': _get_ps_generated,
        'payslips': _get_payslips,
        'payment_started': _get_payment_started,
        'closed': _get_closed,
        'br100': _get_br100,
        'br50': _get_br50,
        'br10': _get_br10,
        'br5': _get_br5,
        'br1': _get_br1,
        'cent50': _get_cent50,
        'cent25': _get_cent25,
        'cent10': _get_cent10,
        'cent05': _get_cent05,
        'cent01': _get_cent01,
        'exact_change': _get_change_total,
        'ps_amendments_conf': _get_confirmed_amendments,
        'ps_amendments_draft': _get_draft_amendments,
    }

    def reload(self, cr, uid, ids, context=None):

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context
        }

    def view_alerts(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)

        employee_ids = []
        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period:
                [employee_ids.append(c.employee_id.id)
                 for c in period.schedule_id.contract_ids]
            else:
                return {}
        else:
            return {}

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.schedule.alert',
            'domain': [
                ('employee_id', 'in', employee_ids),
                '&',
                ('name', '>=', period.date_start),
                ('name', '<=', period.date_end),
            ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context
        }

    def view_payroll_exceptions(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)

        ex_obj = self.pool.get('hr.payslip.exception')
        run_obj = self.pool.get('hr.payslip.run')

        ex_ids = []
        slip_ids = []
        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period:
                for run_id in period.register_id.run_ids:
                    data = run_obj.read(
                        cr, uid, run_id.id, ['slip_ids'], context=context)
                    [slip_ids.append(i) for i in data['slip_ids']]
                ex_ids = ex_obj.search(
                    cr, uid, [('slip_id', 'in', slip_ids)], context=context)

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip.exception',
            'domain': [('id', 'in', ex_ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context
        }

    def _do_recalc_alerts(self, cr, uid, ids, context=None):

        alert_obj = self.pool.get('hr.schedule.alert')

        if context is None:
            context = {}
        period_id = context.get('active_id', False)

        if period_id:
            period = self.pool.get('hr.payroll.period').browse(
                cr, uid, period_id, context=context)
            if period:
                employee_ids = []
                [employee_ids.append(c.employee_id.id)
                 for c in period.schedule_id.contract_ids]

                dtStart = datetime.strptime(
                    period.date_start, '%Y-%m-%d %H:%M:%S')
                dtEnd = datetime.strptime(period.date_end, '%Y-%m-%d %H:%M:%S')

                dtNext = dtStart
                while dtNext <= dtEnd:
                    for employee_id in employee_ids:
                        alert_obj.compute_alerts_by_employee(
                            cr, uid, employee_id,
                            dtNext.date().strftime(
                                '%Y-%m-%d'),
                            context=context)
                    dtNext += relativedelta(days=+1)

    def recalc_alerts(self, cr, uid, ids, context=None):

        self._do_recalc_alerts(cr, uid, ids, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'context': context
        }

    def lock_period(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return

        # TODO - should not be necessary any more
        # Make sure to re-calculate alerts first. Just in case.
        # self._do_recalc_alerts(cr, uid, ids, context=context)

        data = self.read(cr, uid, ids[0], ['alert_critical'], context=context)
        if data.get('alert_critical') != 0:
            raise orm.except_orm(
                _('Unable to Lock the Payroll Period'),
                _('There are one or more Critical Severity Exceptions. '
                  'Please correct them before proceeding.')
            )

        wkf_service = netsvc.LocalService('workflow')
        wkf_service.trg_validate(
            uid, 'hr.payroll.period', period_id, 'lock_period', cr)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'context': context
        }

    def _remove_register(self, cr, uid, register_id, context=None):

        reg_obj = self.pool.get('hr.payroll.register')
        run_obj = self.pool.get('hr.payslip.run')
        slip_obj = self.pool.get('hr.payslip')
        reg_data = reg_obj.read(
            cr, uid, register_id, ['run_ids'], context=context)
        for run_id in reg_data['run_ids']:
            run_data = run_obj.read(
                cr, uid, run_id, ['slip_ids'], context=context)
            slip_obj.unlink(cr, uid, run_data['slip_ids'], context=context)
        run_obj.unlink(cr, uid, reg_data['run_ids'], context=context)
        reg_obj.unlink(cr, uid, register_id, context=context)

    def unlock_period(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return

        # Re-wind pay period if we are in payslip generation state
        #
        p_data = self.pool.get('hr.payroll.period').read(
            cr, uid, period_id,
            ['state', 'register_id'],
            context=context)
        if p_data['state'] == 'generate':
            self._remove_register(
                cr, uid, p_data['register_id'][0], context=context)

        wkf_service = netsvc.LocalService('workflow')
        wkf_service.trg_validate(
            uid, 'hr.payroll.period', period_id, 'unlock_period', cr)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'context': context
        }

    def create_payroll_register(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return

        # Get relevant data from the period object
        period_obj = self.pool.get('hr.payroll.period')
        p_data = period_obj.read(cr, uid, period_id,
                                 ['name', 'date_start', 'date_end',
                                     'schedule_id', 'register_id', 'state'],
                                 context=context)

        if p_data['state'] not in ['locked', 'generate']:
            raise orm.except_orm(_('Invalid Action'), _(
                'You must lock the payroll period first.'))

        # Remove any pre-existing payroll registers
        if p_data['register_id']:
            self._remove_register(cr, uid, p_data['register_id'][0], context)

        # Create the payroll register
        register_obj = self.pool.get('hr.payroll.register')
        register_id = register_obj.create(cr, uid, {
            'name': p_data['name'] + ': Register',
            'date_start': p_data['date_start'],
            'date_end': p_data['date_end'],
        }, context=context)

        # Get list of departments and list of contracts for this period's
        # schedule
        r_data = register_obj.read(
            cr, uid, register_id, ['company_id'], context=context)

        department_ids = self.pool.get('hr.department').search(
            cr, uid,
            [('company_id', '=', r_data['company_id'][0])],
            context=context)
        s_data = self.pool.get(
            'hr.payroll.period.schedule').read(
                cr, uid, p_data['schedule_id'][0],
                ['contract_ids', 'tz'], context=context)

        # Create payslips for employees, in all departments,
        # that have a contract in this
        # pay period's schedule
        self.create_payslip_runs(
            cr, uid, register_id, department_ids, s_data['contract_ids'],
            s_data['tz'], context=context)

        # Attach payroll register to this pay period
        period_obj.write(cr, uid, period_id, {
                         'register_id': register_id}, context=context)

        # Trigger re-calculation of exact change
        self._change_res['done'] = False

        # Mark the pay period as being in the payroll generation stage
        netsvc.LocalService('workflow').trg_validate(
            uid, 'hr.payroll.period', period_id, 'generate_payslips', cr)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'context': context
        }

    def create_payslip_runs(
        self, cr, uid, register_id, dept_ids, contract_ids, tz, context=None
    ):

        contract_obj = self.pool.get('hr.contract')
        dept_obj = self.pool.get('hr.department')
        ee_obj = self.pool.get('hr.employee')
        slip_obj = self.pool.get('hr.payslip')
        run_obj = self.pool.get('hr.payslip.run')
        reg_obj = self.pool.get('hr.payroll.register')
        pr = reg_obj.browse(cr, uid, register_id, context=context)

        # DateTime in db is store as naive UTC. Convert it to explicit UTC
        # and then convert
        # that into the time zone of the pay period schedule.
        #
        local_tz = timezone(tz)
        utc_tz = timezone('UTC')
        utcDTStart = utc_tz.localize(
            datetime.strptime(pr.date_start, '%Y-%m-%d %H:%M:%S'))
        loclDTStart = utcDTStart.astimezone(local_tz)
        date_start = loclDTStart.strftime('%Y-%m-%d')
        utcDTEnd = utc_tz.localize(
            datetime.strptime(pr.date_end, '%Y-%m-%d %H:%M:%S'))
        loclDTEnd = utcDTEnd.astimezone(local_tz)
        date_end = loclDTEnd.strftime('%Y-%m-%d')

        # Get Pay Slip Amendments, Employee ID, and the amount of the amendment
        #
        psa_codes = []
        psa_ids = self._get_confirmed_amendments(cr, uid, context)
        for psa in self.pool.get('hr.payslip.amendment').browse(
            cr, uid, psa_ids, context=context
        ):
            psa_codes.append(
                (psa.employee_id.id, psa.input_id.code, psa.amount))

        # Keep track of employees that have already been included
        seen_ee_ids = []

        # Create payslip batch (run) for each department
        #
        for dept in dept_obj.browse(cr, uid, dept_ids, context=context):
            ee_ids = []
            contracts_dict = {}
            c_ids = contract_obj.search(cr, uid, [
                ('id', 'in', contract_ids),
                '|',
                ('department_id.id', '=', dept.id),
                ('employee_id.department_id.id', '=', dept.id)
            ], context=context)
            c2_ids = contract_obj.search(
                cr, uid, [
                    ('id', 'in', contract_ids),
                    '|',
                    ('job_id.department_id.id', '=', dept.id),
                    ('end_job_id.department_id.id', '=', dept.id),
                ], context=context)
            for i in c2_ids:
                if i not in c_ids:
                    c_ids.append(i)

            c_data = contract_obj.read(
                cr, uid, c_ids, ['employee_id'], context=context)
            for data in c_data:
                if contracts_dict.get(data['employee_id'][0], False):
                    contracts_dict[data['employee_id'][0]].append(data['id'])
                else:
                    contracts_dict.update(
                        {data['employee_id'][0]: [data['id']]})
                if data['employee_id'][0] not in ee_ids:
                    ee_ids.append(data['employee_id'][0])

            if len(ee_ids) == 0:
                continue

            # Alphabetize
            ee_ids = ee_obj.search(
                cr, uid, [('id', 'in', ee_ids)], context=context)

            run_res = {
                'name': dept.complete_name,
                'date_start': date_start,
                'date_end': date_end,
                'register_id': register_id,
            }
            run_id = run_obj.create(cr, uid, run_res, context=context)

            # Create a pay slip for each employee in each department that has
            # a contract in the pay period schedule of this pay period
            #
            slip_ids = []
            for ee in ee_obj.browse(cr, uid, ee_ids, context=context):

                if ee.id in seen_ee_ids:
                    continue

                found_contract = False
                for contract in ee.contract_ids:

                    # Does employee have a contract in this pay period?
                    #
                    dContractStart = datetime.strptime(
                        contract.date_start, OEDATE_FORMAT).date()
                    dContractEnd = loclDTEnd.date()
                    if contract.date_end:
                        dContractEnd = datetime.strptime(
                            contract.date_end, OEDATE_FORMAT).date()
                    if (
                        dContractStart > loclDTEnd.date() or
                        dContractEnd < loclDTStart.date()
                    ):
                        continue
                    elif contract.id in contracts_dict[ee.id]:
                        found_contract = contract
                        break
                if not found_contract:
                    continue

                # If the contract doesn't cover the full pay period use
                # the contract
                # dates as start/end dates instead of the full period.
                #
                temp_date_start = date_start
                temp_date_end = date_end
                if dContractStart > datetime.strptime(
                    date_start, OEDATE_FORMAT
                ).date():
                    temp_date_start = dContractStart.strftime(OEDATE_FORMAT)
                if (
                    found_contract.date_end and
                    dContractEnd < datetime.strptime(
                        date_end, OEDATE_FORMAT).date()
                ):
                    temp_date_end = dContractEnd.strftime(OEDATE_FORMAT)

                slip_data = slip_obj.onchange_employee_id(
                    cr, uid, [],
                    temp_date_start, temp_date_end,
                    ee.id, contract_id=False,
                    context=context)

                # Make modifications to rule inputs
                #
                for line in slip_data['value'].get('input_line_ids', False):

                    # Pay Slip Amendment modifications
                    for eid, code, amount in psa_codes:
                        if eid == ee.id and line['code'] == code:
                            line['amount'] = amount
                            break

                res = {
                    'employee_id': ee.id,
                    'name': slip_data['value'].get('name', False),
                    'struct_id': slip_data['value'].get('struct_id', False),
                    'contract_id': slip_data['value'].get(
                        'contract_id', False),
                    'payslip_run_id': run_id,
                    'input_line_ids': [
                        (0, 0, x) for x in slip_data['value'].get(
                            'input_line_ids', False)
                    ],
                    'worked_days_line_ids': [
                        (0, 0, x)
                        for x
                        in slip_data['value'].get(
                            'worked_days_line_ids', False)
                    ],
                    'date_from': date_start,
                    'date_to': date_end
                }
                slip_ids.append(slip_obj.create(cr, uid, res, context=context))

                seen_ee_ids.append(ee.id)

            # Calculate payroll for all the pay slips in this batch (run)
            slip_obj.compute_sheet(cr, uid, slip_ids, context=context)

        return

    def view_payroll_register(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get(
            'hr.payroll.period').read(cr, uid, period_id, ['register_id'],
                                      context=context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.register',
            'res_id': p_data['register_id'][0],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True,
            'context': context,
        }

    def start_payments(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        # Do not continue if there are still any critical payroll exceptions
        #
        data = self.read(cr, uid, ids[0], ['pex_critical'], context=context)
        if data.get('pex_critical') != 0:
            raise orm.except_orm(
                _('Unable to Start Payments'),
                _('There are one or more Critical Payroll Exceptions. '
                  'Please correct them before proceeding.'))

        p_data = self.pool.get('hr.payroll.period').read(
            cr, uid, period_id,
            ['state', 'register_id'],
            context=context)
        if p_data['state'] != 'generate':
            return {'type': 'ir.actions.act_window_close'}

        wkf_service = netsvc.LocalService('workflow')

        # Set Pay Slip Amendments to Done
        #
        psa_ids = self._get_confirmed_amendments(cr, uid, context)
        [wkf_service.trg_validate(
            uid, 'hr.payslip.amendment', psa_id, 'payslip_done', cr)
         for psa_id in psa_ids]

        # Verify Pay Slips
        #
        reg_obj = self.pool.get('hr.payroll.register')
        reg_data = reg_obj.read(
            cr, uid, p_data['register_id'][0], ['run_ids'], context=context)
        for run_id in reg_data['run_ids']:
            run_data = self.pool.get('hr.payslip.run').read(
                cr, uid, run_id,
                ['slip_ids'], context=context)
            [wkf_service.trg_validate(
                uid, 'hr.payslip', slip_id, 'hr_verify_sheet', cr)
             for slip_id in run_data['slip_ids']]

        wkf_service.trg_validate(
            uid, 'hr.payroll.period', period_id, 'start_payments', cr)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period.end.1',
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'context': context
        }

    def print_payslips(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get(
            'hr.payroll.period').read(cr, uid, period_id, ['register_id'],
                                      context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.payroll.register.payslips',
            'datas': {'ids': [p_data['register_id'][0]]},
        }

    def print_payroll_summary(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get(
            'hr.payroll.period').read(cr, uid, period_id, ['register_id'],
                                      context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.payroll.register.summary',
            'datas': {'ids': [p_data['register_id'][0]]},
        }

    def print_payroll_register(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get(
            'hr.payroll.period').read(cr, uid, period_id, ['register_id'],
                                      context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_register_report',
            'datas': {'ids': [p_data['register_id'][0]]},
        }

    def print_payslip_details(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get(
            'hr.payroll.period').read(cr, uid, period_id, ['register_id'],
                                      context=context)
        register = self.pool.get(
            'hr.payroll.register').browse(cr, uid, p_data['register_id'][0],
                                          context=context)
        slip_ids = []
        for run in register.run_ids:
            [slip_ids.append(s.id) for s in run.slip_ids]

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payslip',
            'datas': {'ids': slip_ids},
        }

    def print_contribution_registers(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        data = self.pool.get(
            'hr.payroll.period').read(
                cr, uid, period_id, ['date_start', 'date_end'],
                context=context)
        register_ids = self.pool.get('hr.contribution.register').search(
            cr, uid, [], context=context)

        form = {'date_from': data['date_start'],
                'date_to': data['date_end'], }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'contribution.register.lines',
            'datas': {
                'ids': register_ids, 'form': form,
                'model': 'hr.contribution.register'},
        }

    def close_pay_period(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        period_id = context.get('active_id', False)
        if not period_id:
            return {'type': 'ir.actions.act_window_close'}

        p_data = self.pool.get('hr.payroll.period').read(cr, uid, period_id,
                                                         ['state'],
                                                         context=context)
        if p_data['state'] != 'payment':
            return {'type': 'ir.actions.act_window_close'}

        wkf_service = netsvc.LocalService('workflow')
        wkf_service.trg_validate(
            uid, 'hr.payroll.period', period_id, 'close_period', cr)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.period',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context
        }
