# Copyright 2010-2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

UPDATE_PARTNER_FIELDS = ['firstname', 'lastname', 'user_id', 'address_home_id']


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_name(self, lastname, firstname):
        return self.env['res.partner']._get_computed_name(lastname, firstname)

    @api.onchange('firstname', 'lastname')
    def _onchange_firstname_lastname(self):
        if self.firstname and self.lastname:
            self.name = self._get_name(self.lastname, self.firstname)

    def _firstname_default(self):
        return ' ' if self.env.context.get('module') else False

    firstname = fields.Char(default=_firstname_default)
    lastname = fields.Char(required=True, default=_firstname_default)

    @api.model
    def create(self, vals):
        if vals.get('firstname') and vals.get('lastname'):
            vals['name'] = self._get_name(vals['lastname'], vals['firstname'])

        elif vals.get('name'):
            vals['lastname'] = self.split_name(vals['name'])['lastname']
            vals['firstname'] = self.split_name(vals['name'])['firstname']
        res = super().create(vals)
        res._update_partner_firstname()
        return res

    @api.multi
    def write(self, vals):
        if vals.get('firstname') or vals.get('lastname'):
            lastname = vals.get('lastname') or self.lastname or ' '
            firstname = vals.get('firstname') or self.firstname or ' '
            vals['name'] = self._get_name(lastname, firstname)
        elif vals.get('name'):
            vals['lastname'] = self.split_name(vals['name'])['lastname']
            vals['firstname'] = self.split_name(vals['name'])['firstname']
        res = super().write(vals)
        if set(vals).intersection(UPDATE_PARTNER_FIELDS):
            self._update_partner_firstname()
        return res

    @api.model
    def split_name(self, name):
        clean_name = " ".join(name.split(None)) if name else name
        return self.env['res.partner']._get_inverse_name(clean_name)

    @api.model
    def _update_employee_names(self):
        employees = self.search([
            ('firstname', '=', ' '),
            ('lastname', '=', ' ')
        ])
        for employee in employees:
            split_name = self.split_name(employee.name)
            employee.write({
                'firstname': split_name['firstname'],
                'lastname': split_name['lastname'],
            })

    def _update_partner_firstname(self):
        for employee in self:
            partners = employee.mapped('user_id.partner_id')
            partners |= employee.mapped('address_home_id')
            partners.write({
                'firstname': employee.firstname,
                'lastname': employee.lastname,
            })
