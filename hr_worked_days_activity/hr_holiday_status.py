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


class hr_holidays_status(orm.Model):
    _inherit = 'hr.holidays.status'
    _columns = {
        'paid_leave': fields.boolean(
            'Is Paid Leave',
            help="Whether this leave is paid or not",
        ),
        'activity_ids': fields.one2many(
            'hr.activity',
            'leave_id',
            'Activity',
        ),
    }
    _defaults = {
        # Creates an leave type automatically
        'activity_ids': [
            {'type': 'leave'}
        ]
    }

    def name_get(self, cr, uid, ids, context=None):
        # There is a missing context check in
        # addons/hr_holidays/hr_holidays.py
        # This is fixed by a patch in v8.
        context = context or {}
        return super(hr_holidays_status, self).name_get(
            cr, uid, ids, context=context)
