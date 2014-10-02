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


class account_analytic_activity_rel(orm.Model):
    _name = 'account.analytic.activity.rel'
    _description = 'Relation object between analytic accounts and activities'
    _columns = {
        'analytic_account_id': fields.many2one(
            'account.analytic.account',
            'Analytic Account'
        ),
        'activity_id': fields.many2one(
            'hr.analytic.timesheet.activity',
            'Activity'
        ),
    }


class account_analytic_account(orm.Model):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _columns = {
        'authorized_activity_ids': fields.many2many(
            'hr.analytic.timesheet.activity',
            'account_analytic_activity_rel',
            'analytic_account_id',
            'activity_id',
            'Authorized Activities',
        )
    }

    def get_authorized_activities(self, cr, uid, account_id, context=None):
        account = self.browse(cr, uid, account_id)
        activities = [
            activity.id for activity in account.authorized_activity_ids
        ]
        return activities
