# -*- coding:utf-8 -*-
from openerp import fields, models, api, _

class HrPayslipAmendment(models.Model):
    _name = 'hr.payslip.amendment'
    _description = 'Pay Slip Amendment'
    _inherit = ['mail.thread']

    name = fields.Char('Description', size=128, required=True, readonly=True, 
                       states={'draft': [('readonly', False)]},)
    date = fields.Date('Effectie Date', required=True, 
                       default=fields.Date.today())
    input_id = fields.Many2one('hr.rule.input', 'Salary Rule Input', 
                               required=True, readonly=True, 
                               states={'draft': [('readonly', False)]},)
    slip_id = fields.Many2one('hr.payslip', 'Paid On', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
        readonly=True, states={'draft': [('readonly', False)]},)
    amount = fields.Float('Amount', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        help="The meaning of this field is dependent on the salary rule "
        "that uses it.")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('validate', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        'State', default='draft', required=True, readonly=True)
    note = fields.Text('Memo')

    @api.onchange('employee_id')
    @api.one
    def onchange_employee(self):
        if len(self.employee_id):
            if self.employee_id.identification_id:
                self.name = _('Pay Slip Amendment: %s (%s)') % \
                                        (self.employee_id.name, 
                                         self.employee_id.identification_id)
            else:
                self.name = _('Pay Slip Amendment: %s') % \
                                        (self.employee_id.name)
    
    @api.multi
    def unlink(self):
        for psa in self:
            if psa.state in ['validate', 'done']:
                raise Warning('A Pay Slip Amendment that has been confirmed '
                              'cannot be deleted!')
        return super(HrPayslipAmendment, self).unlink()
