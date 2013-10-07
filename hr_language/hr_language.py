# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import tools
from osv import osv, fields


class hr_language(osv.osv):
    _name = 'hr.language'
    _columns = {
        'name': fields.selection(tools.scan_languages(),'Language', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'read': fields.boolean('Read'),
        'write': fields.boolean('Write'),
        'speak': fields.boolean('Speak'),
    }

    _defaults = {
        'read': True,
        'write': True,
        'speak': True,
    }
hr_language()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'language_ids': fields.one2many('hr.language', 'employee_id', 'Languages'),
    }
hr_employee()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
