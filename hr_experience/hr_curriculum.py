# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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

from openerp.osv import fields, orm


class hr_curriculum(orm.Model):
    _name = 'hr.curriculum'
    _columns = {
        'name': fields.char('Name', required=True,
                            help="Name"),
        'employee_id': fields.many2one('hr.employee', 'Employee',
                                       required=True,
                                       help="Employee"),
        'start_date': fields.date('Start date',
                                  help="Start date"),
        'end_date': fields.date('End date',
                                help="End date"),
        'description': fields.text('Description'),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                      help="Employer, School, University, Certification Authority"),
        'location': fields.char('Location',
                                help="Location"),
        'expire': fields.boolean('Expire', help="Expire"),

    }

    _defaults = {
        'expire': True,
    }
