#-*- coding:utf-8 -*-
#
#
#    Copyrigth (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
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
#

from openerp.osv import fields, osv


class hr_department(osv.Model):

    _name = 'hr.department'
    _inherit = 'hr.department'

    _columns = {
        'code': fields.char('Code', size=64),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of departments."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'
    _sql_constraints = [
        ('code_uniq', 'unique(code, company_id)', 'The code for the department must be unique per company !'),
    ]

    def name_get(self, cr, uid, ids, context=None):
        """
        Show department code instead of name with:
        <field name="department_id" context="{'show_code': True}"/>
        """
        if not context.get('show_code'):
            return super(hr_department, self).name_get(cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        return [(record.id, record.code) for record in self.browse(cr, uid, ids, context=context or {})]
