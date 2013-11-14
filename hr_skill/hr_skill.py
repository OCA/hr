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
from openerp.osv import fields, orm


class hr_skill(orm.Model):
    _name = 'hr.skill'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'active': fields.boolean('Active'),
        'parent_id': fields.many2one('hr.skill', 'Parent', ondelete='cascade'),
        'child_ids': fields.one2many('hr.skill', 'parent_id', 'Children'),
        'view': fields.selection([('view', 'View'), ('skill', 'Skill')], 'Skill', required=True),
        'employee_ids': fields.many2many('hr.employee', 'skill_employee_rel', 'skill_id', 'employee_id', 'Employee(s)'),
    }
    _defaults = {
        'view': lambda self, cr, uid, context: 'view',
        'active': lambda self, cr, uid, context: 1
    }
hr_skill()


class hr_employee(orm.Model):
    _inherit = 'hr.employee'
    _columns = {
        'skill_ids': fields.many2many('hr.skill', 'skill_employee_rel', 'employee_id', 'skill_id', 'Skills'),
    }
hr_employee()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
