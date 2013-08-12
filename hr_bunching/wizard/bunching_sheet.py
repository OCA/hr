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

from openerp.osv import fields, osv

class bunching_sheet(osv.TransientModel):
    
    _name = 'hr.bunching.sheet.sheet'
    _description = 'Bunching Sheet Recording Format'
    
    _columns = {
        'name': fields.date('Date', required=True, readonly=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True, readonly=True),
        'recorder_id': fields.many2one('hr.employee', 'Prepared By', required=True, readonly=True),
        'line_ids': fields.one2many('hr.bunching.sheet.sheet.line', 'sheet_id', 'Bunching Records'),
    }
    
    def _get(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        sheet_id = context.get('active_id', False)
        return  self.pool.get('hr.bunching.sheet').read(cr, uid, sheet_id,
                                                        ['name', 'department_id', 'recorder_id'],
                                                        context=context)
    
    def _get_name(self, cr, uid, context=None):
        
        return self._get(cr, uid, context=context)['name']
    
    def _get_department(self, cr, uid, context=None):
        
        return self._get(cr, uid, context=context)['department_id'][0]
    
    def _get_recorder(self, cr, uid, context=None):
        
        return self._get(cr, uid, context=context)['recorder_id'][0]

    def _get_lines(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        
        e_obj = self.pool.get('hr.employee')
        sheet_obj = self.pool.get('hr.bunching.sheet')
        sheet_id = context.get('active_id', False)
        department_id =  self.pool.get('hr.bunching.sheet').browse(cr, uid, sheet_id,
                                                                   context=context).department_id.id
        res = []
        
        e_ids = e_obj.search(cr, uid,
                             [('department_id', '=', department_id)],
                             context=context)
        sheet = sheet_obj.browse(cr, uid, sheet_id, context=context)
        for eid in e_ids:
            vals = {
                    'employee_id': eid,
            }
            if sheet:
                for line in sheet.line_ids:
                    if line.employee_id.id != eid:
                        continue
                    for rou in line.round_ids:
                        if rou.qty > 0:
                            vals['round'+str(rou.round)+'_qty'] = rou.qty
                        
            res.append(vals)
        return res
    
    _defaults = {
        'name': _get_name,
        'recorder_id': _get_recorder,
        'department_id': _get_department,
        'line_ids': _get_lines,
    }
    
    def add_records(self, cr, uid, ids, context=None):
        
        sheet_obj = self.pool.get('hr.bunching.sheet')
        
        sheet_id = context.get('active_id', False)
        sheet_obj.action_delete_lines(cr, uid, [sheet_id], context=context)
        data = self.read(cr, uid, ids[0], ['line_ids'], context=context)
        for line in self.pool.get('hr.bunching.sheet.sheet.line').browse(cr, uid, data['line_ids'],
                                                                         context=context):
            if line.subtotal < 1:
                continue
            
            round_vals = []
            if line.round1_qty:
                round_vals.append((0, 0, {'round': 1, 'qty': line.round1_qty}))
            if line.round2_qty:
                round_vals.append((0, 0, {'round': 2, 'qty': line.round2_qty}))
            if line.round3_qty:
                round_vals.append((0, 0, {'round': 3, 'qty': line.round3_qty}))
            if line.round4_qty:
                round_vals.append((0, 0, {'round': 4, 'qty': line.round4_qty}))
            if line.round5_qty:
                round_vals.append((0, 0, {'round': 5, 'qty': line.round5_qty}))
            if line.round6_qty:
                round_vals.append((0, 0, {'round': 6, 'qty': line.round6_qty}))
            if line.round7_qty:
                round_vals.append((0, 0, {'round': 7, 'qty': line.round7_qty}))
            if line.round8_qty:
                round_vals.append((0, 0, {'round': 8, 'qty': line.round8_qty}))
            if line.round9_qty:
                round_vals.append((0, 0, {'round': 9, 'qty': line.round9_qty}))
            if line.round10_qty:
                round_vals.append((0, 0, {'round': 10, 'qty': line.round10_qty}))
            if line.round11_qty:
                round_vals.append((0, 0, {'round': 11, 'qty': line.round11_qty}))
            if line.round12_qty:
                round_vals.append((0, 0, {'round': 12, 'qty': line.round12_qty}))
            if line.round13_qty:
                round_vals.append((0, 0, {'round': 13, 'qty': line.round13_qty}))
            if line.round14_qty:
                round_vals.append((0, 0, {'round': 14, 'qty': line.round14_qty}))
            if line.round15_qty:
                round_vals.append((0, 0, {'round': 15, 'qty': line.round15_qty}))
            if line.round16_qty:
                round_vals.append((0, 0, {'round': 16, 'qty': line.round16_qty}))
            if line.round17_qty:
                round_vals.append((0, 0, {'round': 17, 'qty': line.round17_qty}))
            if line.round18_qty:
                round_vals.append((0, 0, {'round': 18, 'qty': line.round18_qty}))
            if line.round19_qty:
                round_vals.append((0, 0, {'round': 19, 'qty': line.round19_qty}))
            if line.round20_qty:
                round_vals.append((0, 0, {'round': 20, 'qty': line.round20_qty}))
            
            line_val = {
                'name': line.employee_id.name + ': ' + line.sheet_id.name,
                'employee_id': line.employee_id.id,
                'sheet_id': sheet_id,
                'round_ids': round_vals,
            }
            sheet_obj.write(cr, uid, sheet_id, {'line_ids': [(0, 0, line_val)]}, context=context)
        
        return {'type': 'ir.actions.act_window_close'}

class bunching_line(osv.TransientModel):
    
    _name = 'hr.bunching.sheet.sheet.line'
    _description = 'Bunching Sheet Recording Format Line Item'
    
    def _subtotal(self, cr, uid, ids, field_name, args, context=None):
        
        res = dict.fromkeys(ids, 0)
        for l in self.browse(cr, uid, ids, context=context):
            res[l.id] = l.round1_qty+l.round2_qty+l.round3_qty+l.round4_qty+l.round5_qty+l.round6_qty+l.round7_qty+l.round8_qty+l.round9_qty+l.round10_qty+l.round11_qty+l.round12_qty+l.round13_qty+l.round14_qty+l.round15_qty+l.round16_qty+l.round17_qty+l.round18_qty+l.round19_qty+l.round20_qty
        return res
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'sheet_id': fields.many2one('hr.bunching.sheet.sheet', 'Sheet'),
        'subtotal': fields.function(_subtotal, type='integer', method=True, string='Subtotal'),
        'round1_qty': fields.integer('R01'),
        'round2_qty': fields.integer('R02'),
        'round3_qty': fields.integer('R03'),
        'round4_qty': fields.integer('R04'),
        'round5_qty': fields.integer('R05'),
        'round6_qty': fields.integer('R06'),
        'round7_qty': fields.integer('R07'),
        'round8_qty': fields.integer('R08'),
        'round9_qty': fields.integer('R09'),
        'round10_qty': fields.integer('R10'),
        'round11_qty': fields.integer('R11'),
        'round12_qty': fields.integer('R12'),
        'round13_qty': fields.integer('R13'),
        'round14_qty': fields.integer('R14'),
        'round15_qty': fields.integer('R15'),
        'round16_qty': fields.integer('R16'),
        'round17_qty': fields.integer('R17'),
        'round18_qty': fields.integer('R18'),
        'round19_qty': fields.integer('R19'),
        'round20_qty': fields.integer('R20'),
    }
