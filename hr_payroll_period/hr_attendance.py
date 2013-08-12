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
from openerp.tools.translate import _
from osv import fields, osv

class hr_attendance(osv.osv):
    
    _name = 'hr.attendance'
    _inherit = 'hr.attendance'
    
    _columns = {
        'state': fields.selection((
                                   ('draft', 'Unverified'), ('verified', 'Verified'), ('locked', 'Locked'),
                                  ), 'State', required=True, readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
    }
    
    def create(self, cr, uid, vals, context=None):
        
        ee_data = self.pool.get('hr.employee').read(cr, uid, vals['employee_id'],
                                                    ['contract_ids'], context=context)
        pp_ids = self.pool.get('hr.payroll.period').search(cr, uid,
                                                           [
                                                            ('state', 'in', ['locked','generate','payment','closed']),                                                            
                                                            ('schedule_id.contract_ids', 'in', ee_data['contract_ids']),
                                                            '&', ('date_start', '<=', vals['name']),
                                                                 ('date_end', '>=', vals['name']),
                                                           ], context=context)
        if len(pp_ids) > 0:
            raise osv.except_osv(_('The period is Locked!'),
                                 _('You may not add an attendace record to a locked period.'))
        
        return super(hr_attendance, self).create(cr, uid, vals, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        for punch in self.browse(cr, uid, ids, context=context):
            if punch.state in ['verified', 'locked']:
                raise osv.except_osv(_('The Record cannot be deleted!'), _('You may not delete a record that is in a %s state:\nEmployee: %s, Date: %s, Action: %s') %(punch.state, punch.employee_id.name, punch.name, punch.action))
        
        return super(hr_attendance, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        for punch in self.browse(cr, uid, ids, context=context):
            if punch.state in ['verified', 'locked'] and (vals.get('name', False) or vals.get('action', False) or vals.get('employee_id', False)):
                raise osv.except_osv(_('The record cannot be modified!'), _('You may not write to a record that is in a %s state:\nEmployee: %s, Date: %s, Action: %s') %(punch.state, punch.employee_id.name, punch.name, punch.action))
        
        return super(hr_attendance, self).write(cr, uid, ids, vals, context=context)
