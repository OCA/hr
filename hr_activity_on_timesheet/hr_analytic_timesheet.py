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


class hr_analytic_timesheet(orm.Model):
    _inherit = 'hr.analytic.timesheet'
    _columns = {
        'activity_id': fields.many2one(
            'hr.activity',
            'Activity',
            required=True,
        ),
    }

    _defaults = {
        'activity_id': lambda self, cr, uid, context=None:
        self.pool['hr.payslip.worked_days']._get_default_activity(
            cr, uid, context=context)
    }

    def on_change_account_id(
        self, cr, uid, ids,
        account_id, user_id=False, activity_id=False,
        context=None
    ):
        # on_change_account_id in module hr_timesheet_invoice does
        # not accept the context argument, so we don't pass it with super
        res = super(hr_analytic_timesheet, self).on_change_account_id(
            cr, uid, ids, account_id, user_id=user_id)

        if 'value' not in res:
            res['value'] = {}

        # If an activity and an account are given, check if the activity
        # is authorized for the account. If the activity is authorized,
        # return the same activity_id.
        if not activity_id:
            res['value']['activity_id'] = False

        elif account_id:
            account_data = self.pool['account.analytic.account'].read(
                cr, uid, account_id, [
                    'authorized_activity_ids', 'activity_type'],
                context=context)

            auth_act_ids = account_data['authorized_activity_ids']
            activity_type = account_data['activity_type']

            activity = self.pool['hr.activity'].browse(
                cr, uid, activity_id, context=context)

            if activity_id in auth_act_ids or (
                not auth_act_ids and activity_type == activity.type
            ):
                res['value']['activity_id'] = activity_id
            else:
                res['value']['activity_id'] = False

        return res
