# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Salton Massally <salton.massally@gmail.com>.
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


from datetime import datetime

from openerp import models, fields, api, _


class EmploymentInactivate(models.TransientModel):

    _name = 'hr.employment.end'
    _description = 'Employee De-Activation Wizard'

    date = fields.Date(
        'Effective Date',
        required=True,
    )
    reason_id = fields.Many2one(
        'hr.employee.termination.reason',
        'Reason',
        required=True
    )
    notes = fields.Text(
        'Notes',
        required=True
    )

    @api.multi
    def apply(self):
        self.ensure_one()
        vals = {
            'name': self.date,
            'employee_id': self.env.context.get('active_id'),
            'reason_id': self.reason_id.id,
            'notes': self.notes,
        }
        self.env['hr.employee.termination'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
