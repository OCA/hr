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

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    remaining_leaves = fields.Integer(
        readonly=True
    )

    @api.one
    @api.depends('date_start', 'initial_employment_date', 'leaves_count')
    def _compute_remaining_days(self):
        '''
        we want the cache to invalidate this any of the fields listed as
        dependency is cahnged
        '''
        return super(HrEmployee, self)._compute_remaining_days()
