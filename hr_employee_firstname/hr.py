# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp.osv import orm, fields


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def _auto_init(self, cr, context=None):
        """pre-create and fill column lastname so that the constraint
        setting will not fail"""
        self._field_create(cr, context=context)
        column_data = self._select_column_data(cr)
        if 'lastname' not in column_data:
            field = self._columns['lastname']
            cr.execute('ALTER TABLE "%s" ADD COLUMN "lastname" %s' %
                       (self._table,
                        orm.pg_varchar(field.size)))
            cr.execute('UPDATE hr_employee '
                       'SET lastname = name_related '
                       'WHERE name_related IS NOT NULL')
        return super(hr_employee, self)._auto_init(cr, context=context)

    def create(self, cursor, uid, vals, context=None):
        firstname = vals.get('firstname')
        lastname = vals.get('lastname')
        if firstname or lastname:
            names = (firstname, lastname)
            vals['name'] = " ".join(s for s in names if s)
        else:
            vals['lastname'] = vals['name']
        return super(hr_employee, self).create(
            cursor, uid, vals, context=context)

    _columns = {
        'firstname': fields.char("Firstname"),
        'lastname': fields.char("Lastname", required=True)
    }
