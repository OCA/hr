# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .hr_fiscal_year import get_schedules


class HrPeriod(models.Model):
    _name = 'hr.period'
    _inherit = 'date.range'
    _description = 'HR Payroll Period'
    _order = 'date_start'

    @api.model
    def _default_type(self, company_id=False):
        if not company_id:
            company_id = self.env.user.company_id.id
        period_type = self.env['date.range.type'].search(
            [('hr_period', '=', True),
             ('company_id', '=', company_id)], limit=1)
        return period_type

    name = fields.Char(
        'Name',
        required=True,
        states={'draft': [('readonly', False)]}
    )
    number = fields.Integer(
        'Number',
        required=True,
        states={'draft': [('readonly', False)]}
    )
    date_payment = fields.Date(
        'Date of Payment',
        required=True,
        states={'draft': [('readonly', False)]}
    )
    fiscalyear_id = fields.Many2one(
        'hr.fiscalyear',
        'Fiscal Year',
        required=True,
        states={'draft': [('readonly', False)]},
        ondelete='cascade'
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('done', 'Closed')
        ],
        'Status',
        required=True,
        default='draft'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        related="fiscalyear_id.company_id",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    schedule_pay = fields.Selection(
        get_schedules,
        'Scheduled Pay',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    payslip_ids = fields.One2many(
        'hr.payslip',
        'hr_period_id',
        'Payslips',
        readonly=True
    )

    type_id = fields.Many2one(
        domain=[('hr_period', '=', True)],
        default=_default_type
    )

    @api.model
    def get_next_period(self, company_id, schedule_pay):
        """
         Get the next payroll period to process
        :rtype: hr.period browse record
        """
        period = self.search([
            ('company_id', '=', company_id),
            ('schedule_pay', '=', schedule_pay),
            ('state', '=', 'open'),
        ], order='date_start', limit=1)
        return period if period else False

    @api.multi
    def button_set_to_draft(self):
        for period in self:
            if period.payslip_ids:
                raise UserError(
                    _('You can not set to draft a period that already '
                        'has payslips computed'))

        self.write({'state': 'draft'})

    @api.multi
    def button_open(self):
        self.write({'state': 'open'})

    @api.multi
    def button_close(self):
        self.write({'state': 'done'})
        for period in self:
            fy = period.fiscalyear_id

            # If all periods are closed, close the fiscal year
            if all(p.state == 'done' for p in fy.period_ids):
                fy.write({'state': 'done'})

    @api.multi
    def button_re_open(self):
        self.write({'state': 'open'})
        for period in self:
            fy = period.fiscalyear_id
            if fy.state != 'open':
                fy.write({'state': 'open'})
