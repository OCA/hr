#-*- coding:utf-8 -*-
##############################################################################
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
##############################################################################

from datetime import datetime

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

class hr_bunching(osv.Model):
    
    _name = 'hr.bunching.sheet'
    _description = 'Bunching sheet from the grading hall'
    
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _total(self, cr, uid, ids, field_name, arg, context=None):
        
        res = dict.fromkeys(ids, 0)
        for sheet in self.browse(cr, uid, ids, context=context):
            for line in sheet.line_ids:
                res[sheet.id] += line.difference > 0 and line.difference or 0
        return res
    
    _columns = {
        'name': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department', required=True, domain=[('name', 'ilike', '%grading%')], readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}),
        'recorder_id': fields.many2one('hr.employee', 'Prepared By', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}),
        'line_ids': fields.one2many('hr.bunching.sheet.line', 'sheet_id', 'Bunching Lines', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirmed'),
                                   ('approve', 'Approved'),
                                  ],
                                  'State', readonly=True),
        'total': fields.function(_total, type='integer', method=True, string='Difference Total'),
    }
    
    _defaults = {
        'name': datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT),
        'state': 'draft',
    }
    
    _order = 'name desc'
    
    _sql_constraints = [
        ('unique_dept_date', 'UNIQUE(name,department_id)', _('Duplicate entry for Department and Date!')),
    ]
    
    _track = {
        'state': {
            'hr_bunching.mt_alert_confirmed': lambda self, cr,uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_bunching.mt_alert_approved': lambda self, cr,uid, obj, ctx=None: obj['state'] == 'approve',
        },
    }
    
    def _needaction_domain_get(self, cr, uid, context=None):
        
        domain = []
        if self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state','=','confirm')]
        
        if len(domain) == 0:
            return False
        
        return domain
    
    def onchange_department(self, cr, uid, ids, department_id, context=None):
        
        res = {'domain': {'recorder_id': False}}
        if department_id:
            res['domain']['recorder_id'] = [('department_id', '=', department_id)]
        return res
    
    def action_delete_lines(self, cr, uid, ids, context=None):
        
        line_obj = self.pool.get('hr.bunching.sheet.line')
        line_ids = line_obj.search(cr, uid, [('sheet_id', 'in', ids)], context=context)
        if len(line_ids) > 0:
            line_obj.unlink(cr, uid, line_ids, context=context)
        return True

class hr_bunch_line(osv.Model):
    
    _name = 'hr.bunching.sheet.line'
    _description = 'Bunching sheet line items'
    
    def _calculate(self, cr, uid, ids, field_name, arg, context=None):
        
        res = dict.fromkeys(ids)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {'total': 0, 'difference': 0}
            for r in line.round_ids:
                res[line.id]['total'] += r.qty
            res[line.id]['difference'] = res[line.id]['total'] - line.bunching_quota
        
        return res
    
    _columns = {
        'name': fields.char('Description', size=64, required=True, readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True),
        'sheet_id': fields.many2one('hr.bunching.sheet', 'Bunching Sheet', ondelete='cascade', required=True, readonly=True),
        'round_ids': fields.one2many('hr.bunching.sheet.line.round', 'line_id', 'Rounds'),
        'total': fields.function(_calculate, type='integer', method=True, string='Total',
                                 multi='total', required=True),
        'difference': fields.function(_calculate, type='integer', method=True, string='Difference',
                                      multi='total', readonly=True),
        'bunching_quota': fields.integer('Goal', readonly=True),
    }

class hr_bunch_line_round(osv.Model):
    
    _name = 'hr.bunching.sheet.line.round'
    _description = 'Bunching sheet line rounds'
    
    _columns = {
        'round': fields.integer('Round', required=True),
        'qty': fields.integer('Quantity', required=True),
        'line_id': fields.many2one('hr.bunching.sheet.line', 'Bunching Sheet Line', ondelete='cascade', required=True),
    }
