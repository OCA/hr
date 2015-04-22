# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, fields, api


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    @api.one
    def _default_employee(self):
        if self._context.get('search_default_employee_id', False)
            return self._context['search_default_employee_id']

    employee_id = fields.Many2one("hr.employee",
                                  string="Employee",
                                  required=True,
                                  default="_get_default_employee")
    employee_dept_id = fields.Many2one("hr.department",
                                       string="Department",
                                       related="employee_id.department_id")
    state = fields.Selection(
            [
             ('draft', 'Draft'),
             ('approve', 'Approved'),
             ('decline', 'Declined'),
            ],
            string='State',
            default='draft',
            readonly=True,
        )

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.employee_dept_id = self.employee_id.department_id
