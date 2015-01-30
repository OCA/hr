# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
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

from openerp.osv import fields, orm


class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'authorized_activity_ids': fields.many2many(
            'hr.activity',
            'account_analytic_activity_rel',
            'analytic_account_id',
            'activity_id',
            'Authorized Activities',
        ),
        'activity_type': fields.selection(
            (
                ('leave', 'Leaves'),
                ('job', 'Job Positions'),
            ),
            'Activity Type',
            required=True,
        ),
    }

    _defaults = {
        'activity_type': 'job',
    }
