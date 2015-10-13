# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields, orm


class hr_payroll_run(orm.Model):

    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    _columns = {
        'register_id': fields.many2one('hr.payroll.register', 'Register'),
    }


class hr_payroll_register(orm.Model):

    _name = 'hr.payroll.register'

    _columns = {
        'name': fields.char('Description', size=256),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('close', 'Close'),
        ], 'Status', select=True, readonly=True),
        'date_start': fields.datetime(
            'Date From', required=True, readonly=True,
            states={'draft': [('readonly', False)]}
        ),
        'date_end': fields.datetime(
            'Date To', required=True, readonly=True,
            states={'draft': [('readonly', False)]}
        ),
        'run_ids': fields.one2many(
            'hr.payslip.run', 'register_id', readonly=True,
            states={'draft': [('readonly', False)]}
        ),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
            _('Payroll Register description must be unique.')),
    ]

    def _get_default_name(self, cr, uid, context=None):

        nMonth = datetime.now().strftime('%B')
        year = datetime.now().year
        name = _('Payroll for the Month of %s %s' % (nMonth, year))
        return name

    def _get_company(self, cr, uid, context=None):

        users_pool = self.pool.get('res.users')
        return users_pool.browse(cr, uid,
                                 users_pool.search(
                                     cr, uid, [(
                                         'id', '=', uid)], context=context),
                                 context=context)[0].company_id.id

    _defaults = {
        'name': _get_default_name,
        'state': 'draft',
        'company_id': _get_company,
    }

    def action_delete_runs(self, cr, uid, ids, context=None):

        pool = self.pool.get('hr.payslip.run')
        ids = pool.search(
            cr, uid, [('register_id', 'in', ids)], context=context)
        pool.unlink(cr, uid, ids, context=context)
        return True
