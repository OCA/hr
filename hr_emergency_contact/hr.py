#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from osv import fields, osv

class hr_employee(osv.osv):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
                'ec_name': fields.char('Name', size=256),
                'ec_relationship': fields.char('Relationship', size=64),
                'ec_tel1': fields.char('Primary Phone No.', size=32),
                'ec_tel2': fields.char('Secondary Phone No.', size=32),
                'ec_woreda': fields.char('Subcity/Woreda', size=32),
                'ec_kebele': fields.char('Kebele', size=8),
                'ec_houseno': fields.char('House No.', size=8),
                'ec_address': fields.char('Address 2', size=256),
                'ec_country_id': fields.many2one('res.country', 'Country'),
                'ec_state_id': fields.many2one('res.country.state', 'State', domain="[('country_id','=',country_id)]"),
    }
    
    def _get_country(self, cr, uid, context=None):
        cid = self.pool.get('res.country').search(cr, uid, [('code','=','ET')], context=context)
        return cid[0]
    
    _defaults = {
        'ec_country_id': _get_country,
    }

