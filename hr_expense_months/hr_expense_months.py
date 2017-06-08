# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DT_FORMAT

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class hr_expense_expense(osv.osv):
    _inherit = "hr.expense.expense"
    _columns = {
        'date': fields.date('Date', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'user_valid': fields.many2one('res.users', 'Validation By', readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'department_id':fields.many2one('hr.department','Department', readonly=True, states={'draft':[('readonly',False)]}),   
        'note': fields.text('Note', readonly=True,states={'draft':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Force Journal', help = "The journal used when the expense is done.", readonly=True,states={'draft':[('readonly',False)]}),
        'account_move_id': fields.many2one('account.move', 'Ledger Posting', readonly=True,states={'draft':[('readonly',False)]}),     
        'name': fields.selection([
            ('Janvier', 'January'),
            ('Fevrier', 'February'),
            ('Mars', 'March'),
            ('Avril', 'April'),
            ('Mai', 'May'),
            ('Juin', 'June'),
	     ('Juillet', 'July'),
	     ('Aout', 'August'),
	     ('Septembre', 'September'),
	     ('Octobre', 'October'),
	     ('Novembre', 'November'),
	     ('Decembre', 'December'),],
            'Months',required=True,states={'draft':[('readonly',False)]}),
        'months': fields.selection([
            ('Janvier', 'January'),
            ('Fevrier', 'February'),
            ('Mars', 'March'),
            ('Avril', 'April'),
            ('Mai', 'May'),
            ('Juin', 'June'),
	     ('Juillet', 'July'),
	     ('Aout', 'August'),
	     ('Septembre', 'September'),
	     ('Octobre', 'October'),
	     ('Novembre', 'November'),
	     ('Decembre', 'December'),],
            'Months',readonly=True,required=True,states={'draft':[('readonly',False)]}),
    }

    def onchange_months(self, cr, uid, ids, mois):
        result={}
        result['name']=mois
        return {'value': result}

hr_expense_expense()

class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"
    _order = "date_value"
    
hr_expense_line()
