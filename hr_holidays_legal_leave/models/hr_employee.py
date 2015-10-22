# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, api, fields
from openerp.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _inverse_remaining_days(self):
        legal_leave = self.company_id.legal_holidays_status_id
        if not legal_leave:
            raise UserWarning('Legal/annual leave type is not defined for '
                              'your company')
        diff = self.remaining_leaves - legal_leave.get_days(
            self.id)[legal_leave.id]['remaining_leaves']
        if diff > 0:
            leave = self.env['hr.holidays'].create(
                {
                    'name': 'Allocation for %s' % self.name,
                    'employee_id': self.id,
                    'holiday_status_id': legal_leave.id,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'number_of_days_temp': diff
                }
            )
        elif diff < 0:
            raise UserWarning(
                'You cannot reduce validated allocation requests')

        for sig in ('confirm', 'validate', 'second_validate'):
            leave.signal_workflow(sig)

    @api.one
    def _compute_remaining_days(self):
        legal_leave = self.company_id.legal_holidays_status_id
        if not legal_leave:
            raise UserWarning('Legal/annual leave type is not defined for '
                              'your company')
        self.remaining_leaves = legal_leave.get_days(
            self.id)[legal_leave.id]['remaining_leaves']

    remaining_leaves = fields.Integer(
        'Remaining Legal Leaves',
        compute='_compute_remaining_days',
        inverse='_inverse_remaining_days',
        help='Total number of legal leaves allocated to this employee, '
             'change this value to create allocation/leave request. '
             'Total based on all the leave types without overriding limit.'
    )
