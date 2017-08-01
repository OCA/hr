# -*- coding:utf-8 -*-
# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from .hr_fiscal_year import get_schedules


class HrPeriod(models.Model):
    _name = 'hr.period'
    _inherit = 'date.range'
    _description = 'HR Payroll Period'
    _order = 'date_start'

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    number = fields.Integer(
        'Number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_payment = fields.Date(
        'Date of Payment',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    fiscalyear_id = fields.Many2one(
        'hr.fiscalyear',
        'Fiscal Year',
        required=True,
        readonly=True,
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
        readonly=True,
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
