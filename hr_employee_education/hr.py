# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
#

from datetime import datetime

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT

EDUCATION_SELECTION = [
    ('none', 'No Education'),
    ('primary', 'Primary School'),
    ('secondary', 'Secondary School'),
    ('diploma', 'Diploma'),
    ('degree1', 'First Degree'),
    ('masters', 'Masters Degree'),
    ('phd', 'PhD'),
]


class hr_employee(orm.Model):

    _inherit = 'hr.employee'

    def _calculate_age(self, cr, uid, ids, field_name, arg, context=None):

        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.birthday:
                dBday = datetime.strptime(ee.birthday, OE_DFORMAT).date()
                dToday = datetime.now().date()
                res[ee.id] = (dToday - dBday).days / 365
        return res

    _columns = {
        'education': fields.selection(EDUCATION_SELECTION, 'Education'),
        'age': fields.function(_calculate_age, type='integer', method=True, string='Age'),
    }
