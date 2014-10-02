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
from openerp.osv import orm
from openerp.tools.translate import _


class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def timesheet_mapping(self, timesheets, payslip, date_from, date_to):
        worked_days = {}
        for ts in timesheets:
            for act in ts.timesheet_ids:
                if date_from <= act.date <= date_to:
                    act_id = act.activity_id.id
                    if (ts.id, act_id) in worked_days:
                        worked_days[(ts.id, act_id)]['number_of_hours'] \
                            += act.unit_amount
                    else:
                        worked_days[(ts.id, act_id)] = {
                            'name': _('Timesheet ') + ' ' + ts.date_from,
                            'number_of_hours': 0,
                            'contract_id': payslip.contract_id.id,
                            'code': 'TS',
                            'imported_from_timesheet': True,
                            'activity_id': act_id,
                        }

        return worked_days
