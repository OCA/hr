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


import time
from datetime import datetime

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    inactive_ids = fields.One2many(
        'hr.employee.termination',
        'employee_id',
        'Deactivation Records'
    )

    @api.multi
    def end_employment_wizard(self):
        self.ensure_one()

        # let's ensure that we do not currently have a pending termination rec
        # in place; if we do we want to return that
        termination = self.env['hr.employee.termination'].search(
            [
                ('employee_id', '=', self.id),
                ('state', 'in', ('draft', 'confirm'))
            ],
            limit=1,
        )
        if termination:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.termination',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': termination.id
            }
        else:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employment.end',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_employee_id': self.id}
            }

    @api.multi
    def end_employment(self, effective_date=None):
        effective_date = effective_date or fields.Date.today()
        # let's ensure that all open contracts are closed
        contracts = self.env['hr.contract'].search(
            [
                ('employee_id', 'in', self.ids),
                '|',
                ('date_end', '=', False),
                ('date_end', '>', effective_date),
            ]
        )
        contracts.write({'date_end': effective_date})
        self.write({'active': False})

    @api.multi
    def restart_employment(self):
        self.write({'actvie': True})
