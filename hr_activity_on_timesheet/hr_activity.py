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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class hr_activity(orm.Model):
    _inherit = 'hr.activity'

    def _get_authorized_user_ids(
        self, cr, uid, ids, field_name, args=None, context=None
    ):
        """
        Get the ids of users related to an employee that occupies a job
        position related to an activity.
        """
        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        res = {}
        for activity in self.browse(cr, uid, ids, context=context):
            if activity.type != 'job':
                # In this case, we dont need the list of users.
                res[activity.id] = False
            else:
                contract_jobs = activity.job_id.contract_job_ids
                # Get the list of authorized employees.
                # (employees with a contract that contains a job)
                employees = [
                    j.contract_id.employee_id
                    for j in contract_jobs
                    if j.contract_id.date_start <= now
                    and (
                        not j.contract_id.date_end
                        or now <= j.contract_id.date_end
                    )
                ]

                # Get the list of authorized users from authorized
                # employees.
                res[activity.id] = [
                    employee.user_id.id
                    for employee in employees
                    if employee.user_id
                ]
        return res

    def _search_activities_from_user(
        self, cr, uid, obj, field_name, args=None, context=None
    ):
        """
        Search the activities from a given user id or employee id

        This method is called by a view to get the job positions of
        an employee
        """
        if not context:
            return []

        # The context may contain the user id.
        if 'user_id' in context:
            user = self.pool['res.users'].browse(
                cr, uid, context['user_id'], context=context
            )
            employee = user.employee_ids[0]
        else:
            return []

        # Get the activities related to the jobs
        # on the employee's contract
        activity_ids = [
            contract_job.job_id.activity_ids[0].id
            for contract_job in employee.contract_id.contract_job_ids
            if contract_job.job_id.activity_ids
        ]

        return [('id', 'in', activity_ids)]

    _columns = {
        'authorized_user_ids': fields.function(
            _get_authorized_user_ids,
            fnct_search=_search_activities_from_user,
            method=True,
            relation='res.users',
            type="many2many",
            string="Authorized Users",
        ),
    }
