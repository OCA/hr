# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, osv
from openerp import netsvc


class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    def draft_sheet(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for payslip in ids:
            wf_service.trg_validate(uid, 'hr.payslip', payslip, 'act_cancel', cr)
            return self.write(cr, uid, payslip, {'state': 'draft'},
                              context=context)
