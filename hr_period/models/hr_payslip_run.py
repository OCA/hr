# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .hr_fiscal_year import get_schedules


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda obj: obj.env['ir.sequence']
        .next_by_code('hr.payslip.run')
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        states={'close': [('readonly', True)]},
        default=lambda obj: obj.env.user.company_id
    )
    hr_period_id = fields.Many2one(
        'hr.period',
        string='Period',
        states={'close': [('readonly', True)]}
    )
    date_payment = fields.Date(
        'Date of Payment',
        states={'close': [('readonly', True)]}
    )
    schedule_pay = fields.Selection(
        get_schedules,
        'Scheduled Pay',
        states={'close': [('readonly', True)]}
    )

    @api.multi
    @api.constrains('hr_period_id', 'company_id')
    def _check_period_company(self):
        for run in self:
            if run.hr_period_id:
                if run.hr_period_id.company_id != run.company_id:
                    raise UserError(_(
                        "The company on the selected period must be the same "
                        "as the company on the payslip batch."))

    @api.multi
    @api.constrains('hr_period_id', 'schedule_pay')
    def _check_period_schedule(self):
        for run in self:
            if run.hr_period_id:
                if run.hr_period_id.schedule_pay != run.schedule_pay:
                    raise UserError(_("""The schedule on the selected period
                        must be the same as the schedule on the
                        payslip batch."""))

    @api.model
    def get_default_schedule(self, company_id):
        company = self.env['res.company'].browse(company_id)

        fys = self.env['hr.fiscalyear'].search([('state', '=', 'open'),
                                                ('company_id', '=', company.id)
                                                ])
        return (
            fys[0].schedule_pay
            if fys else 'monthly'
        )

    @api.multi
    @api.onchange('company_id', 'schedule_pay')
    def onchange_company_id(self):
        self.ensure_one()
        schedule_pay = self.schedule_pay or self.get_default_schedule(
            self.company_id.id)
        if self.company_id and schedule_pay:
            period = self.env['hr.period'].get_next_period(self.company_id.id,
                                                           schedule_pay,)
            self.hr_period_id = period.id if period else False,

    @api.onchange('hr_period_id')
    def onchange_period_id(self):
        period = self.hr_period_id
        if period:
            self.date_start = period.date_start
            self.date_end = period.date_end
            self.date_payment = period.date_payment
            self.schedule_pay = period.schedule_pay

    @api.model
    def create(self, vals):
        """
        Keep compatibility between modules
        """
        if vals.get('date_end') and not vals.get('date_payment'):
            vals.update({'date_payment': vals['date_end']})
        return super(HrPayslipRun, self).create(vals)

    @api.multi
    def get_payslip_employees_wizard(self):
        """ Replace the static action used to call the wizard
        """
        self.ensure_one()
        view = self.env.ref('hr_payroll.view_hr_payslip_by_employees')

        company = self.company_id

        employee_ids = self.env['hr.employee'].search(
            [('company_id', '=', company.id),
             ('contract_id.schedule_pay', '=', self.schedule_pay)]).ids

        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Payslips'),
            'res_model': 'hr.payslip.employees',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_company_id': company.id,
                'default_schedule_pay': self.schedule_pay,
                'default_employee_ids': [(6, 0, employee_ids)],
            }
        }

    @api.multi
    def close_payslip_run(self):
        for run in self:
            if next((p for p in run.slip_ids if p.state == 'draft'), False):
                raise UserError(_("The payslip batch %s still has unconfirmed "
                                "pay slips." % run.name))
        self.update_periods()
        return super(HrPayslipRun, self).close_payslip_run()

    @api.multi
    def draft_payslip_run(self):
        for run in self:
            run.hr_period_id.button_re_open()
        return super(HrPayslipRun, self).draft_payslip_run()

    @api.multi
    def update_periods(self):
        self.ensure_one()
        period = self.hr_period_id
        if period:
            # Close the current period
            period.button_close()

            # Open the next period of the fiscal year
            fiscal_year = period.fiscalyear_id
            next_period = fiscal_year.search_period(
                number=period.number + 1)
            if next_period:
                next_period.button_open()
