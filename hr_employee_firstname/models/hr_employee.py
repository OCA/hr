# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import models, fields, api, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def split_name(self, name):
        new_name = [w for w in name.split(' ') if w]
        firstname = new_name[0]
        lastname = ' '.join(new_name[1:]) or ' '
        return firstname, lastname

    @api.cr_context
    def _auto_init(self, cr, context=None):
        super(HrEmployee, self)._auto_init(cr, context=context)
        self._update_employee_names(cr, SUPERUSER_ID, context=context)

    @api.model
    def _update_employee_names(self):
        employees = self.search([
            ('firstname', '=', ' '), ('lastname', '=', ' ')])

        for ee in employees:
            firstname, lastname = self.split_name(ee.name)
            ee.write({
                'firstname': firstname,
                'lastname': lastname,
            })

    @api.one
    @api.onchange('firstname', 'lastname')
    def get_name(self):
        if self.firstname and self.lastname:
            self.name = ' '.join([self.firstname, self.lastname])

    def _firstname_default(self):
        return ' ' if self.env.context.get('module') else False

    firstname = fields.Char(
        "Firstname", required=True, default=_firstname_default)
    lastname = fields.Char(
        "Lastname", required=True, default=_firstname_default)

    @api.model
    def create(self, vals):
        if vals.get('firstname') and vals.get('lastname'):
            vals['name'] = ' '.join([vals['firstname'], vals['lastname']])

        elif vals.get('name'):
            vals['firstname'], vals['lastname'] = self.split_name(vals['name'])

        return super(HrEmployee, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('firstname') or vals.get('lastname'):
            self.ensure_one()

            vals['name'] = ' '.join([
                vals.get('firstname') or self.firstname or ' ',
                vals.get('lastname') or self.lastname or ' ',
            ])

        elif vals.get('name'):
            vals['firstname'], vals['lastname'] = self.split_name(vals['name'])

        return super(HrEmployee, self).write(vals)
