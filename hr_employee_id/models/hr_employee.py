# -*- coding: utf-8 -*-
# © 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
import string
from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = 'hr.employee'

    identification_id = fields.Char(
        string='Identification No',
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
            employee_id = company.employee_id_sequence.next_by_id()
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
    def create(self, vals):
        if not vals.get('identification_id'):
            vals['identification_id'] = self._generate_identification_id()
        return super(HrEmployee, self).create(vals)
