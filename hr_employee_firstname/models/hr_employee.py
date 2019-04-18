# Copyright 2010-2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

UPDATE_PARTNER_FIELDS = ['firstname', 'lastname', 'user_id', 'address_home_id']


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_name(self, lastname, firstname):
        return self.env['res.partner']._get_computed_name(lastname, firstname)

    @api.onchange('firstname', 'lastname')
    def _onchange_firstname_lastname(self):
        if self.firstname or self.lastname:
            self.name = self._get_name(self.lastname, self.firstname)

    firstname = fields.Char()
    lastname = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('firstname') or vals.get('lastname'):
            vals['name'] = self._get_name(
                vals.get('lastname'), vals.get('firstname'))
        elif vals.get('name'):
            vals['lastname'] = self.split_name(vals['name'])['lastname']
            vals['firstname'] = self.split_name(vals['name'])['firstname']
        else:
            raise ValidationError(_('No name set.'))
        res = super(HrEmployee, self).create(vals)
        self._update_partner_firstname(res)
        return res

    @api.multi
    def write(self, vals):
        if 'firstname' in vals or 'lastname' in vals:
            if 'lastname' in vals:
                lastname = vals.get('lastname')
            else:
                lastname = self.lastname
            if 'firstname' in vals:
                firstname = vals.get('firstname')
            else:
                firstname = self.firstname
            vals['name'] = self._get_name(lastname, firstname)
        elif vals.get('name'):
            vals['lastname'] = self.split_name(vals['name'])['lastname']
            vals['firstname'] = self.split_name(vals['name'])['firstname']
        res = super(HrEmployee, self).write(vals)
        if set(vals).intersection(UPDATE_PARTNER_FIELDS):
            self._update_partner_firstname(self)
        return res

    @api.model
    def split_name(self, name):
        clean_name = " ".join(name.split(None)) if name else name
        return self.env['res.partner']._get_inverse_name(clean_name)

    @api.model
    def _update_employee_names(self):
        employees = self.search([
            ('firstname', '=', False), ('lastname', '=', False)])

        for ee in employees:
            split_name = self.split_name(ee.name)
            ee.write({
                'firstname': split_name['firstname'],
                'lastname': split_name['lastname'],
            })

    @api.model
    def _update_partner_firstname(self, employee):
        partners = employee.mapped('user_id.partner_id')
        for partner in employee.mapped('address_home_id'):
            if partner not in partners:
                partners += partner
        partners.write({'firstname': employee.firstname,
                        'lastname': employee.lastname})

    @api.constrains("firstname", "lastname")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if not (record.firstname or record.lastname or record.name):
                raise ValidationError(_('No name set.'))
