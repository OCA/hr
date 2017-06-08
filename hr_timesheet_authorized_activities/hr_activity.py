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


class hr_activity(orm.Model):
    _inherit = 'hr.activity'

    def _search_activities_from_user(
        self, cr, uid, obj, field_name, args=None, context=None
    ):
        """
        Search the activities from a given user id

        The analytic account must be given in context
        """
        # Call the method in hr_activity_on_timesheet
        res = super(hr_activity, self)._search_activities_from_user(
            cr, uid, obj, field_name, args=args, context=context)

        if not context.get('account_id') or not res:
            return res

        activity_ids = res[0][2]
        account_data = self.pool['account.analytic.account'].read(
            cr, uid, context['account_id'], ['authorized_activity_ids'],
            context=context)

        activity_ids = [
            act for act in activity_ids
            if act in account_data['authorized_activity_ids']]

        return [('id', 'in', activity_ids)]

    _columns = {
        'authorized_user_ids': fields.function(
            lambda self, cr, uid, ids, field_name, args=None, context=None:
            super(hr_activity, self)._get_authorized_user_ids(
                cr, uid, ids, field_name, args=args, context=context),
            fnct_search=_search_activities_from_user,
            method=True,
            relation='res.users',
            type="many2many",
            string="Authorized Users",
        ),
        'authorized_account_ids': fields.many2many(
            'account.analytic.account',
            'account_analytic_activity_rel',
            'activity_id',
            'analytic_account_id',
            'Authorized Accounts',
        )
    }
