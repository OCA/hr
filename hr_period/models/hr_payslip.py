# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class HrPayslip(orm.Model):
    _inherit = 'hr.payslip'

    _columns = {
        'hr_period_id': fields.many2one(
            'hr.period', string='Period',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'date_payment': fields.date(
            'Date of Payment',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
    }

    def _check_period_company(self, cr, uid, ids, context=None):
        for slip in self.browse(cr, uid, ids, context=context):
            if slip.hr_period_id:
                if slip.hr_period_id.company_id != slip.company_id:
                    return False
        return True

    _constraints = [
        (
            _check_period_company,
            "The company on the selected period must be the same as the "
            "company on the payslip.",
            ['hr_period_id', 'company_id'],
        ),
    ]

    def onchange_company_id(
        self, cr, uid, ids, company_id, contract_id, context=None
    ):
        res = {'value': {}}

        if company_id and contract_id:
            contract = self.pool['hr.contract'].browse(
                cr, uid, contract_id, context=context)
            period = self.pool['hr.period'].get_next_period(
                cr, uid, company_id, contract.schedule_pay,
                context=context)

            res['value'].update({
                'hr_period_id': period.id if period else False,
            })

        return res

    def onchange_contract_id(
        self, cr, uid, ids, date_from, date_to,
        employee_id=False, contract_id=False, context=None
    ):

        res = super(HrPayslip, self).onchange_contract_id(
            cr, uid, ids, date_from, date_to,
            employee_id=employee_id, contract_id=contract_id, context=context)

        if employee_id and contract_id:
            employee = self.pool['hr.employee'].browse(
                cr, uid, employee_id, context=context)
            contract = self.pool['hr.contract'].browse(
                cr, uid, contract_id, context=context)

            period = self.pool['hr.period'].get_next_period(
                cr, uid, employee.company_id.id, contract.schedule_pay,
                context=context)

            res['value'].update({
                'hr_period_id': period.id if period else False,
                'name': _('Salary Slip of %s for %s') % (
                    employee.name, period.name),
            })

        return res

    def onchange_hr_period_id(
        self, cr, uid, ids, hr_period_id, context=None
    ):
        res = {'value': {}}

        if hr_period_id:
            period = self.pool['hr.period'].browse(
                cr, uid, hr_period_id, context=context)

            res['value'].update({
                'date_from': period.date_start,
                'date_to': period.date_stop,
                'date_payment': period.date_payment,
            })

        return res

    def create(self, cr, uid, vals, context=None):
        if vals.get('payslip_run_id'):
            payslip_run = self.pool['hr.payslip.run'].browse(
                cr, uid, vals['payslip_run_id'], context=context)

            employee = self.pool['hr.employee'].browse(
                cr, uid, vals['employee_id'], context=context)

            period = payslip_run.hr_period_id

            vals.update({
                'date_payment': payslip_run.date_payment,
                'hr_period_id': period.id,
                'name': _('Salary Slip of %s for %s') % (
                    employee.name, period.name)
            })

        elif vals.get('date_to') and not vals.get('date_payment'):
            vals['date_payment'] = vals['date_to']

        return super(HrPayslip, self).create(cr, uid, vals, context=context)
