# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv
from osv import fields
import wizard
import pooler

class change_passwd(wizard.interface):
	'''
	OpenERP Wizard
	'''
	form = '''<?xml version="1.0"?>
	<form string="Confirm Passwords">
		<field name="user" attrs="{'readonly':[('check','!=',1)]}"/>
		<field name="oldpwd" password="True"/>
		<field name="newpwd" password="True"/>
		<field name="confirmpwd" password="True"/>
	</form>'''

	fields = {
		'user': dict(string=u'User', type='many2one', relation='res.users', required=True),
        'oldpwd': {'string': 'Old Password', 'type': 'char'},
        'newpwd': {'string': 'New Password', 'type': 'char'},
        'confirmpwd': {'string': 'Confirm Password', 'type': 'char'},
        'check': dict(string='Check', type='boolean', invisible=True)
    }

	def _get_value(self, cr, uid, data, context):
		if uid == 1:
			data['form']['check'] = 1
		else:
			data['form']['check'] = 0
		data['form']['user'] = uid
		return data['form']


	def _check_password(self, cr, uid, data, context):
		if data['form']['newpwd'] == data['form']['confirmpwd']:
			pool_obj = pooler.get_pool(cr.dbname)
			obj_change = pool_obj.get('res.users')
			pwd = obj_change.read(cr, uid, [data['form']['user']],['password'])
			if data['form']['oldpwd'] == pwd[0]['password']:
				obj_change.write(cr, uid, [data['form']['user']], {'password':data['form']['newpwd']})
			else:		
				raise osv.except_osv(_('Verification Error !'), _('Your Old Password is not verified.'))
		else:
			raise osv.except_osv(_('Verification Error !'), _('New Password and Confirm password does not match.'))
		
		return {}
    
	states = {
        'init': {
            'actions': [_get_value],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', 'Cancel'), ('process', 'Change'))},
        },
        'process': {
            'actions': [_check_password],
            'result': {'type': 'state', 'state': 'end'},
        },
    }
change_passwd('change.passwd')
