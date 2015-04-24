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


class hr_employee(orm.Model):
    _inherit = 'hr.employee'
    _columns = {
        'academic_ids': fields.one2many('hr.academic',
                                        'employee_id',
                                        'Academic experiences',
                                        help="Academic experiences"),
        'certification_ids': fields.one2many('hr.certification',
                                             'employee_id',
                                             'Certifications',
                                             help="Certifications"),
        'experience_ids': fields.one2many('hr.experience',
                                          'employee_id',
                                          ' Professional Experiences',
                                          help='Professional Experiences'),
    }
