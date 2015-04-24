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

from openerp import models, fields, api


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.cr_context
    def _auto_init(self, cr, context=None):
        res = super(hr_employee, self)._auto_init(cr, context=context)
        cr.execute("""
SELECT id
FROM hr_employee
WHERE firstname IS NULL AND lastname IS NULL
LIMIT 1""")
        if not cr.fetchone():
            cr.execute("""
UPDATE hr_employee
SET firstname = substr(name_related,
                       1,
                       CASE WHEN strpos(name_related, ' ')-2>0
                           THEN strpos(name_related, ' ')
                           ELSE 2
                       END),
    lastname = substr(name_related,
                      CASE WHEN strpos(name_related, ' ')-2>0
                          THEN strpos(name_related, ' ')
                          ELSE 2
                      END + 1,
                      length(name_related) - \
                      CASE WHEN strpos(name_related, ' ')-2>0
                          THEN strpos(name_related, ' ')
                          ELSE 2
                      END+1)
WHERE name_related IS NOT NULL""")
        return res

    @api.one
    @api.onchange('firstname', 'lastname')
    def get_name(self):
        if self.firstname and self.lastname:
            self.name_related = self.firstname + ' ' + self.lastname

    @api.one
    @api.depends('firstname', 'lastname')
    def _get_name(self):
        if self.firstname and self.lastname:
            self.name_related = self.firstname + ' ' + self.lastname

    firstname = fields.Char("Firstname", required=True)
    lastname = fields.Char("Lastname", required=True)
    name_related = fields.Char(string="Name", readonly=True,
                               compute="_get_name",
                               store=True)

    @api.model
    def create(self, vals):
        if vals.get('firstname', '') and vals.get('lastname', ''):
            vals['name'] = vals['firstname'] + ' ' + vals['lastname']
        return super(hr_employee, self).create(vals)
