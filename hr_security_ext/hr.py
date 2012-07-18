# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis, 2011
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

from osv import fields, osv
import reis_base as util 


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'code': fields.char('Internal code', size=16),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        return util.ext_name_get(self, cr, uid, ids, '[%(code)s] %(name)s', ['code','name'], context=context)
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        return util.ext_name_search(self, cr, user, name, args, operator, context=context, limit=limit, 
                                keys=['code','name'])
hr_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
