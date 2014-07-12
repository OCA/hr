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

import random
import string
from openerp.osv import fields, orm
from openerp.tools.translate import _


class hr_employee(orm.Model):

    """Implement company wide unique identification number."""

    IDLEN = 8

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'employee_no': fields.char('Employee ID',
                                   size=IDLEN,
                                   readonly=True),
        # Formatted version of employee ID
        'f_employee_no': fields.char('Employee ID',
                                     size=IDLEN + 2,
                                     readonly=True),
        'tin_no': fields.char('TIN No', size=10),
    }

    _sql_constraints = [
        ('employeeno_uniq', 'unique(employee_no)',
         'The Employee Number must be unique accross the company(s).'),
        ('tinno_uniq', 'unique(tin_no)',
         'There is already another employee with this TIN number.'),
    ]

    def _check_identification(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.identification_id or obj.tin_no:
            return True
        return False

    def _generate_employeeno(self, cr, uid, arg):
        """Generate a random employee identification number"""

        tries = 0
        max_tries = 50
        eid = False
        while tries < max_tries:
            rnd = random.SystemRandom()
            eid = ''.join(rnd.choice(string.digits)
                          for _ in xrange(self.IDLEN))
            cr.execute(
                '''SELECT employee_no FROM hr_employee WHERE employee_no=%s''', tuple((eid,)))
            res = cr.fetchall()
            if len(res) == 0:
                break

            tries += 1

        if tries == max_tries:
            raise orm.except_orm(
                _('Error'),
                _('Unable to generate an Employee ID number that is unique.')
            )

        return eid

    def create(self, cr, uid, vals, context=None):

        eid = self._generate_employeeno(cr, uid, context)
        vals['employee_no'] = eid
        vals['f_employee_no'] = '%s-%s-%s' % (eid[:2], eid[2:4], eid[4:])
        return super(hr_employee, self).create(cr, uid, vals, context)
