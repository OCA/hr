#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

import time

from osv import osv
from osv import fields
from tools import config
from tools.translate import _
from datetime import datetime
from datetime import timedelta

class hr_payroll_declar(osv.osv):
    '''
    Decleration Form
    '''
    _name = 'hr.payroll.declare'
    _description = 'Decleration Form'
    
    _columns = {
        'name':fields.char('Name', size=1024, required=False),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', required=True),
        'income_sal': fields.float('Income by Salary', digits=(16, int(config['price_accuracy'])), readonly=True),
        'income_ids':fields.one2many('hr.payroll.declare.line', 'income_id', 'Source Of Income', required=False),
        'investment_ids':fields.one2many('hr.payroll.declare.line', 'invest_id', 'Investments', required=False),
        'claim_ids':fields.one2many('hr.payroll.declare.line', 'claim_id', 'Allowance to Claime', required=False),
        'date': fields.date('Date'),
        
        'income': fields.float('Taxable Income', digits=(16, int(config['price_accuracy'])), readonly=True),
        'investment': fields.float('Total Investment', digits=(16, int(config['price_accuracy'])), readonly=True),
        'claims': fields.float('Total Allowance Claims', digits=(16, int(config['price_accuracy'])), readonly=True),
        
        'state':fields.selection([
            ('draft','Draft'),
            ('pending','Waiting for Review'),
            ('pending','Approved by HR'),
            ('done','Confirm'),
        ],'State', select=True, readonly=True),
        'note': fields.text('Description'),   
    }
    
    def get_basic(self, cr, uid, ids, context):
        res = {}
        for rs in self.browse(cr, uid, ids, context):
            period_id = self.pool.get('account.period').search(cr,uid,[('date_start','<=',time.strftime('%Y-%m-%d')),('date_stop','>=',time.strftime('%Y-%m-%d'))])[0]
            fiscalyear_id = self.pool.get('account.period').browse(cr, uid, period_id).fiscalyear_id
            sql_req= '''
                SELECT c.id as id, c.wage as wage, function as function, c.date_start as start, c.date_end as end
                FROM hr_contract c
                  LEFT JOIN hr_employee emp on (c.employee_id=emp.id)
                  LEFT JOIN hr_contract_wage_type cwt on (cwt.id = c.wage_type_id)
                  LEFT JOIN hr_contract_wage_type_period p on (cwt.period_id = p.id)
                WHERE
                  (emp.id=%s) AND
                  (date_start >= %s) AND
                  (date_end IS NULL OR date_end <= %s)
                '''
            cr.execute(sql_req, (rs.employee_id.id, fiscalyear_id.date_start, fiscalyear_id.date_stop))
            contracts = cr.dictfetchall()
            if not contracts:
                raise osv.except_osv(_('Contract Error !'), _('No Contract Defined for : %s ' % (rs.employee_id.name)))
            total = 0.0
            
            line_ids = []
            for lines in rs.claim_ids:
                line_ids += [lines.head_id.id]
            
            for ct in contracts:
                allow = 0.0
                
                d1 = ct['start']
                d2 = ct['end'] or fiscalyear_id.date_stop
                td = datetime.fromtimestamp(time.mktime(time.strptime(d2, '%Y-%m-%d'))) - datetime.fromtimestamp(time.mktime(time.strptime(d1, '%Y-%m-%d')))
                total += (td.days / 30) * ct['wage']
            
#                ct = self.pool.get('hr.contract').browse(cr, uid, ct['id'])
#                for line in ct.function.line_ids:
#                    if line.category_id.id in line_ids:
#                        if line.amount_type == 'fix':
#                            allow += (td.days / 30) * line.amount
#                        elif line.amount_type == 'per':
#                            allow += (total * line.amount)
#                        print 'XXXXXXXXXXXXXXXXXXXXXXX : ', line.name, allow
                        
            res[rs.id] = total
        return res
        
    def write(self, cr, user, ids, vals, context=None):
        res = self.get_basic(cr, user, ids, context)
        for id in ids:
            vals['income_sal'] = res[id]
            super(hr_payroll_declar, self).write(cr, user, [id], vals, context)
            
        return res
    
hr_payroll_declar()

class hr_payroll_declare_line(osv.osv):
    '''
    Decleration Line
    '''
    _name = 'hr.payroll.declare.line'
    _description = 'Decleration Line'
    
    def _function_call(self, cr, uid, ids, field_names, arg, context={}):
        res = {}
        for rs in self.browse(cr, uid, ids, context):
            val = 0.0
            
            if rs.income_id:
                pass
            elif rs.invest_id:
                pass
            elif rs.claim_id:
                if rs.head_id.calc_type == 'min_max':
                    if rs.amount < rs.head_id.min:
                        val = rs.head_id.min
                    elif rs.amount >= rs.head_id.min and rs.amount <= rs.head_id.max:
                        val = rs.amount
                    elif rs.amount > rs.head_id.max:
                        val = rs.head_id.max
                
            res[rs.id] = val
            
        return res
    
    _columns = {
        'name':fields.char('Name', size=64, required=False),
        'note': fields.text('Description'),
        'income_id':fields.many2one('hr.payroll.declare', 'Income', required=False),
        'invest_id':fields.many2one('hr.payroll.declare', 'Investment', required=False),
        'claim_id':fields.many2one('hr.payroll.declare', 'Allowance Claims', required=False),
        'amount': fields.float('Amount', digits=(16, int(config['price_accuracy']))),
        'allow': fields.float('Allowence', digits=(16, int(config['price_accuracy']))),
        'allow_amount': fields.function(_function_call, method=True, type='float', digits=(16, int(config['price_accuracy'])), string='Allow Amount'),
        'head_id':fields.many2one('hr.allounce.deduction.categoty', 'Allowance / Deduction', required=True),
        
    }
hr_payroll_declare_line()


class payment_category(osv.osv):
    '''
    Allowance Deduction Categoty
    '''
    _inherit = 'hr.allounce.deduction.categoty'
        
    _columns = {
        'calc_type':fields.selection([
            ('min_max','Min / Max'),
            ('stmt','List of Calculations'),
            ('range','Selection from Range'),
        ],'Calculation Type', select=True, readonly=False),
        'min': fields.float('Min Value', digits=(16, int(config['price_accuracy']))),
        'max': fields.float('Max Value', digits=(16, int(config['price_accuracy']))),
        
        'stmt_ids':fields.one2many('hr.payroll.declare.stmt', 'category_id', 'Functions', required=False),
        'stmt_select':fields.selection([
            ('min','Minimum'),
            ('max','Maximum'),
            ('avg','Average'),
        ],'Selection Method', select=True, readonly=False),
    }
    _defaults = {
        'stmt_select': lambda *a: 'min',
        'calc_type': lambda *a: 'min_max'
    }
payment_category()

class payment_stmt(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.payroll.declare.stmt'
    _description = 'Payroll Calculations'
    
    _columns = {
        'category_id':fields.many2one('hr.allounce.deduction.categoty', 'Category', required=True),
        'name':fields.char('Expression', size=1024, required=True, readonly=False),
        'sequence': fields.integer('Sequence'),
        'active':fields.boolean('Active', required=False),
    }
    _defaults = {
        'sequence': lambda *a: 5,
        'active': lambda *a: True
    }
payment_stmt()
