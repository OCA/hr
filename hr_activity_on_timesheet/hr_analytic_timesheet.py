# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Amura Consulting. All Rights Reserved.
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


class hr_analytic_timesheet(orm.Model):
    _name = 'hr.analytic.timesheet'
    _inherit = 'hr.analytic.timesheet'
    _columns = {
        'activity_id': fields.many2one(
            'hr.analytic.timesheet.activity', 'Activity', required=True,
        ),
    }

    def onchange_account_id(
        self, cr, uid, ids, account_id, context=None
    ):
        print account_id
        res = {}
        account = self.pool.get('account.analytic.account').browse(
            cr, uid, account_id, context
        )
        auth_act_ids = [act.id for act in account.authorized_activity_ids]

        if auth_act_ids:
            res = {'value': {'activity_id': auth_act_ids[0]}}
        else:
            res = {'value': {'activity_id': 0}}

        res['domain'] = {'activity_id': [('id', 'in', auth_act_ids)]}
        return res
