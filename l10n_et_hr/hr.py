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

class hr_employee(osv.Model):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=512),
    }

class hr_department(osv.Model):
    
    _name = 'hr.department'
    _inherit = 'hr.department'
    
    def ethiopic_name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['ethiopic_name','parent_id'], context=context)
        res = []
        for record in reads:
            ethiopic_name = record['ethiopic_name']
            if record['parent_id']:
                readen = self.read(cr, uid, record['parent_id'][0], ['ethiopic_name'], context=context)
                ethiopic_name = readen['ethiopic_name'] + ' / ' + ethiopic_name
            res.append((record['id'], ethiopic_name))
        return res

    def _dept_ethiopic_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.ethiopic_name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=512),
        'complete_ethiopic_name': fields.function(_dept_ethiopic_name_get_fnc, type="char", string='Name'),
    }

class hr_job(osv.Model):
    
    _name = 'hr.job'
    _inherit = 'hr.job'
    
    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=512),
    }
