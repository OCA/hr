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

from .hr_fiscal_year import get_schedules


class HrPayslipRun(orm.Model):
    _inherit = 'hr.payslip.run'

    _columns = {
        'company_id': fields.many2one(
            'res.company', 'Company',
            states={'close': [('readonly', True)]}
        ),
        'hr_period_id': fields.many2one(
            'hr.period', string='Period',
            states={'close': [('readonly', True)]}
        ),
        'date_payment': fields.date(
            'Date of Payment',
            states={'close': [('readonly', True)]}
        ),
        'schedule_pay': fields.selection(
            get_schedules, 'Scheduled Pay',
            states={'close': [('readonly', True)]}
        ),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c={}:
        self.pool['res.users'].browse(
            cr, uid, uid, context=c).company_id.id,
        'name': lambda self, cr, uid, c={}:
        self.pool['ir.sequence'].get(cr, uid, 'hr.payslip.run'),
    }

    def _check_period_company(self, cr, uid, ids, context=None):
        for run in self.browse(cr, uid, ids, context=context):
            if run.hr_period_id:
                if run.hr_period_id.company_id != run.company_id:
                    return False
        return True

    def _check_period_schedule(self, cr, uid, ids, context=None):
        for run in self.browse(cr, uid, ids, context=context):
            if run.hr_period_id:
                if run.hr_period_id.schedule_pay != run.schedule_pay:
                    return False
        return True

    _constraints = [
        (
            _check_period_company,
            "The company on the selected period must be the same as the "
            "company on the payslip batch.",
            ['hr_period_id', 'company_id'],
        ),
        (
            _check_period_schedule,
            "The schedule on the selected period must be the same as the "
            "schedule on the payslip batch.",
            ['hr_period_id', 'schedule_pay'],
        ),
    ]

    def get_default_schedule(self, cr, uid, company_id, context=None):
        company = self.pool['res.company'].browse(
            cr, uid, company_id, context=context)

        fy_obj = self.pool['hr.fiscalyear']

        fy_ids = fy_obj.search(cr, uid, [
            ('state', '=', 'open'),
            ('company_id', '=', company.id),
        ], context=context)

        return (
            fy_obj.browse(cr, uid, fy_ids[0], context=context).schedule_pay
            if fy_ids else 'monthly'
        )

    def onchange_company_id(
        self, cr, uid, ids, company_id, schedule_pay, context=None
    ):
        res = {'value': {}}

        schedule_pay = schedule_pay or self.get_default_schedule(
            cr, uid, company_id, context=context)

        if company_id:
            period = self.pool['hr.period'].get_next_period(
                cr, uid, company_id, schedule_pay,
                context=context)

            res['value'].update({
                'hr_period_id': period.id if period else False,
            })

        return res

    def onchange_period_id(
        self, cr, uid, ids, hr_period_id, context=None
    ):
        res = {'value': {}}

        if hr_period_id:
            period = self.pool['hr.period'].browse(
                cr, uid, hr_period_id, context=context)

            res['value'].update({
                'date_start': period.date_start,
                'date_end': period.date_stop,
                'date_payment': period.date_payment,
                'schedule_pay': period.schedule_pay,
            })

        return res

    def create(self, cr, uid, vals, context=None):
        """ Keep compatibility between modules
        """
        if vals.get('date_end') and not vals.get('date_payment'):
            vals.update({'date_payment': vals['date_end']})

        return super(HrPayslipRun, self).create(cr, uid, vals, context=context)

    def get_payslip_employees_wizard(self, cr, uid, ids, context=None):
        """ Replace the static action used to call the wizard
        """
        payslip_run = self.browse(cr, uid, ids[0], context=context)

        view_ref = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'hr_payroll', 'view_hr_payslip_by_employees')

        view_id = view_ref and view_ref[1] or False

        company = payslip_run.company_id

        employee_obj = self.pool['hr.employee']

        employee_ids = employee_obj.search(cr, uid, [
            ('company_id', '=', company.id),
        ], context=context)

        employee_ids = [
            emp.id for emp in
            employee_obj.browse(cr, uid, employee_ids, context=context)
            if emp.contract_id.schedule_pay == payslip_run.schedule_pay
        ]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Payslips'),
            'res_model': 'hr.payslip.employees',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_company_id': company.id,
                'default_schedule_pay': payslip_run.schedule_pay,
                'default_employee_ids': [(6, 0, employee_ids)],
            }
        }

    def close_payslip_run(self, cr, uid, ids, context=None):
        for run in self.browse(cr, uid, ids, context=context):
            if next((p for p in run.slip_ids if p.state == 'draft'), False):
                raise orm.except_orm(
                    'Warning',
                    'The payslip batch %s still has unconfirmed pay slips.' %
                    run.name)

        self.update_periods(cr, uid, ids, context=context)
        return super(HrPayslipRun, self).close_payslip_run(
            cr, uid, ids, context=context)

    def draft_payslip_run(self, cr, uid, ids, context=None):
        for run in self.browse(cr, uid, ids, context=context):
            run.hr_period_id.button_re_open()

        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def update_periods(self, cr, uid, ids, context=None):
        for run in self.browse(cr, uid, ids, context=context):
            period = run.hr_period_id

            if period:
                # Close the current period
                period.button_close()

                # Open the next period of the fiscal year
                fiscal_year = period.fiscalyear_id
                next_period = fiscal_year.search_period(
                    number=period.number + 1)

                if next_period:
                    next_period.button_open()
