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


class hr_analytic_timesheet_activity(orm.Model):
    _name = 'hr.analytic.timesheet.activity'
    _description = 'Activities for timesheet lines'

    def _get_activity_name(
        self, cr, uid, ids,
        field_name=False, arg=False,
        context=False
    ):
        res = {}

        if isinstance(ids, (int, long)):
            ids = [ids]
        for i in ids:
            activity = self.browse(cr, uid, i)
            if activity.type == 'job' and activity.job_id:
                res[i] = activity.job_id.name
            elif activity.type == 'leave' and activity.leave_id:
                res[i] = activity.leave_id.name
            else:
                res[i] = ''
        return res

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        #remove False from list
        ids = [i for i in ids if i]
        res = [
            (
                act.id,
                self._get_activity_name(
                    cr, uid,
                    act.id,
                    context=context,
                )[act.id]
            ) for act in self.browse(cr, uid, ids)
        ]
        return res

    def onchange_activity_type(self, cr, uid, ids):
        return {
            'value': {
                'job_id': 0,
                'leave_id': 0,
            }
        }

    _columns = {
        'name': fields.function(
            _get_activity_name,
            string='Activity Name',
            method=True,
            type="char",
        ),
        'type': fields.selection(
            (
                ('leave', 'Leave'),
                ('job', 'Job'),
            ),
            'Activity Type',
            required=True,
        ),
        # one2one relations are deprecated in openerp, so I create two many2one
        # fields and put a unique sql constraint on both fields
        'job_id': fields.many2one(
            'hr.job',
            'Job',
        ),
        'leave_id': fields.many2one(
            'hr.holidays.status',
            'Leave Type',
        ),
    }
    _sql_constraints = [
        (
            'job_id_uniq',
            'unique(job_id)',
            'An activity already exists for this job!'
        ),
        (
            'leave_id_uniq',
            'unique(leave_id)',
            'An activity already exists for this leave type!'
        ),
    ]

    _order = 'type'
