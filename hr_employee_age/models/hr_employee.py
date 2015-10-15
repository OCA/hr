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
from datetime import datetime

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    age = fields.Integer(
        'Age',
        readonly=True,
        compute='_compute_age'
    )

    @api.one
    def _compute_age(self):
        if self.birthday:
            dBday = datetime.strptime(self.birthday, OE_DFORMAT).date()
            dToday = datetime.now().date()
            self.age = dToday.year - dBday.year - ((
                dToday.month, dToday.day) < (dBday.month, dBday.day))
