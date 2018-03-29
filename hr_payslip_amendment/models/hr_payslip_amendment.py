# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError


class HrPayslipAmendment(models.Model):
    _name = 'hr.payslip.amendment'
    _description = 'Pay Slip Amendment'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Description',
        size=128,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date = fields.Date(
        'Effectie Date',
        required=True,
        default=fields.Date.today()
    )
    category_id = fields.Many2one(
        'hr.payslip.amendment.category',
        'Category',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    input_id = fields.Many2one(
        'hr.rule.input',
        'Salary Rule Input',
        store=True,
        readonly=True,
        related="category_id.input_rule_id"
    )
    slip_id = fields.Many2one(
        'hr.payslip',
        'Paid On',
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount = fields.Float(
        'Amount',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="The meaning of this field is dependent on the salary rule "
        "that uses it."
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('validate', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        'State',
        default='draft',
        required=True,
        readonly=True
    )
    note = fields.Text('Memo')

    @api.onchange('employee_id')
    @api.one
    def onchange_employee(self):
        if self.employee_id:
            if self.employee_id.identification_id:
                self.name = _('Pay Slip Amendment: %s (%s)') % (
                    self.employee_id.name,
                    self.employee_id.identification_id
                )
            else:
                self.name = _('Pay Slip Amendment: %s') % (
                    self.employee_id.name
                )

    @api.multi
    def unlink(self):
        for psa in self:
            if psa.state in ['validate', 'done']:
                raise UserError('A Pay Slip Amendment that has been confirmed'
                                ' cannot be deleted!')
        return super(HrPayslipAmendment, self).unlink()
