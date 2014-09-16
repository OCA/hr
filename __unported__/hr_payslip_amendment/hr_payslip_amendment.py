#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
#

from openerp.tools.translate import _
from osv import fields, osv


class hr_payslip_amendment(osv.osv):

    _name = 'hr.payslip.amendment'
    _description = 'Pay Slip Amendment'

    _inherit = ['mail.thread']

    _columns = {
        'name': fields.char('Description', size=128, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'input_id': fields.many2one('hr.rule.input', 'Salary Rule Input', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.float('Amount', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="The meaning of this field is dependant on the salary rule that uses it."),
        'state': fields.selection((('draft', 'Draft'),
                                   ('validate', 'Confirmed'),
                                   ('cancel', 'Cancelled'),
                                   ('done', 'Done'),
                                   ), 'State', required=True, readonly=True),
        'note': fields.text('Memo'),
    }

    _defaults = {
        'state': 'draft',
    }

    def onchange_employee(self, cr, uid, ids, employee_id, context=None):

        if not employee_id:
            return {}
        ee = self.pool.get('hr.employee').browse(
            cr, uid, employee_id, context=context)
        name = _('Pay Slip Amendment: %s (%s)') % (ee.name, ee.employee_no)
        val = {'name': name}
        return {'value': val}

    def unlink(self, cr, uid, ids, context=None):

        for psa in self.browse(cr, uid, ids, context=context):
            if psa.state in ['validate', 'done']:
                raise osv.except_osv(_('Invalid Action'),
                                     _('A Pay Slip Amendment that has been confirmed cannot be deleted!'))

        return super(hr_payslip_amendment, self).unlink(cr, uid, ids, context=context)
