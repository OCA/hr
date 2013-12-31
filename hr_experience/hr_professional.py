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


class hr_professional(orm.Model):
    _name = 'hr.professional'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'start_date': fields.date('Start date'),
        'end_date': fields.date('End date'),
        'description': fields.text('Description', translate=True),
        'partner_id': fields.many2one('res.partner', 'Employer'),
        'location': fields.char('Location', size=64, translate=True),
        'expire': fields.boolean('Expire'),
    }

    _defaults = {
        'expire': True,
    }


class hr_employee(orm.Model):
    _inherit = 'hr.employee'
    _columns = {
        'professional_ids': fields.one2many('hr.professional', 'employee_id', ' Professional Experiences'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
