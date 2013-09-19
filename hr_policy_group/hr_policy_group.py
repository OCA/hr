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

class policy_groups(osv.Model):
    
    _name = 'hr.policy.group'
    _description = 'HR Policy Groups'
    
    _columns = {
        'name': fields.char('Name', size=128),
        'contract_ids': fields.one2many('hr.contract', 'policy_group_id', 'Contracts'),
    }

class contract_init(osv.Model):
    
    _inherit = 'hr.contract.init'
    
    _columns = {
        'policy_group_id': fields.many2one('hr.policy.group', 'Policy Group', readonly=True,
                                           states={'draft': [('readonly', False)]}),
    }

class hr_contract(osv.Model):
    
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    _columns = {
        'policy_group_id': fields.many2one('hr.policy.group', 'Policy Group'),
    }
    
    def _get_policy_group(self, cr, uid, context=None):
        
        res = False
        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.policy_group_id:
            res = init.policy_group_id.id
        return res
    
    _defaults = {
        'policy_group_id': _get_policy_group,
    }
