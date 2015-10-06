# -*- coding:utf-8 -*-
from openerp import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    hr_period_id = fields.Many2one(
                                   'hr.period', 
                                   string='Period', 
                                   readonly=True,
                                   states={'draft': [('readonly', False)]}
                                   )
    date_payment = fields.Date(
                               'Date of Payment',
                               readonly=True,
                               states={'draft': [('readonly', False)]}
                               )
    
    @api.multi
    @api.constrains('hr_period_id', 'company_id')
    def _check_period_company(self):
        for slip in self:
            if slip.hr_period_id:
                if slip.hr_period_id.company_id != slip.company_id:
                    raise Warning("The company on the selected period must be "
                                  "the same as the company on the payslip.")
        return True
    
    @api.onchange('company_id', 'contract_id')
    def onchange_company_id(self):
        if len(self.company_id) and len(self.contract_id):
            contract = self.contract_id
            period = self.env['hr.period'].get_next_period(self.company_id.id,
                                                        contract.schedule_pay)
            self.hr_period_id = period.id if period else False
    
    @api.onchange('contract_id')    
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
 
    
    @api.onchange('hr_period_id')
    def onchange_hr_period_id(self):
        if len(self.hr_period_id):
            period = self.hr_period_id
            self.date_from = period.date_start
            self.date_to = period.date_stop
            self.date_payment = period.date_payment

    @api.model
    def create(self, vals):
        if vals.get('payslip_run_id'):
            payslip_run = self.env['hr.payslip.run'].browse(
                                                    vals['payslip_run_id'])

            employee = self.env['hr.employee'].browse(vals['employee_id'])
            period = payslip_run.hr_period_id

            vals['date_payment'] = payslip_run.date_payment
            vals['hr_period_id'] = period.id
            vals['name'] = _('Salary Slip of %s for %s') % (
                employee.name, period.name)

        elif vals.get('date_to') and not vals.get('date_payment'):
            vals['date_payment'] = vals['date_to']

        return super(HrPayslip, self).create(vals)
