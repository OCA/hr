# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
import random
import string
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = 'hr.employee'

    identification_id = fields.Char(
        'Identification No',
        copy=False
    )

    _sql_constraints = [
        ('identification_id_uniq', 'unique(identification_id)',
         'The Employee Number must be unique across the company(s).'),
    ]

    @api.model
    def _generate_identification_id(self):
        """Generate a random employee identification number"""
        company = self.env.user.company_id
        employee_id = False
        if company.employee_id_gen_method == 'sequence':
            employee_id = self.env['ir.sequence'].get_id(
                company.employee_id_sequence.id)
        elif company.employee_id_gen_method == 'random':
            employee_id_random_digits = company.employee_id_random_digits
            tries = 0
            max_tries = 50
            while tries < max_tries:
                rnd = random.SystemRandom()
                employee_id = ''.join(rnd.choice(string.digits)
                                      for _ in
                                      xrange(employee_id_random_digits))
                if not self.search_count([('identification_id',
                                           '=',
                                           employee_id)]):
                    break
                tries += 1
            if tries == max_tries:
                raise UserWarning(_('Unable to generate an Employee ID number that \
                is unique.'))
        return employee_id

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        eid = self._generate_identification_id()
        vals['identification_id'] = eid
        return super(HrEmployee, self).create(vals)
