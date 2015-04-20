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

from openerp import models, fields


class hr_hourly_rate(models.Model):
    _name = 'hr.hourly.rate'
    _description = 'Hourly rate'

    rate = fields.Float(string='Rate', required=True)
    date_start = fields.Date(string='Start Date', required=True,
                             default=fields.Date.today())
    date_end = fields.Date(string='End Date')
    class_id = fields.Many2one('hr.hourly.rate.class',
                               string='Salary Class',
                               ondelete='cascade',
                               required=True)
