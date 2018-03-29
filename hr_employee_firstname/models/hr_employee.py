# -*- coding: utf-8 -*-
# ©  2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

UPDATE_PARTNER_FIELDS = ['firstname', 'lastname', 'user_id', 'address_home_id']


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_whitespace_cleaned_name(self, name, comma=False):
        """Remove redundant whitespace from :param:`name`.

        Removes leading, trailing and duplicated whitespace.
        """
        try:
            name = u" ".join(name.split()) if name else name
        except UnicodeDecodeError:
            # with users coming from LDAP, name can be a str encoded as utf-8
            # this happens with ActiveDirectory for instance, and in that case
            # we get a UnicodeDecodeError during the automatic ASCII -> Unicode
            # conversion that Python does for us.
            # In that case we need to manually decode the string to get a
            # proper unicode string.
            name = u' '.join(name.decode('utf-8').split()) if name else name

        if comma:
            name = name.replace(" ,", ",")
            name = name.replace(", ", ",")
        return name

    @api.model
    def _get_inverse_name(self, name):
        """Compute the inverted name.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Guess name splitting
        order = self._get_names_order()
        # Remove redundant spaces
        name = self._get_whitespace_cleaned_name(
            name, comma=(order == 'last_first_comma'))
        parts = name.split("," if order == 'last_first_comma' else " ", 1)
        if len(parts) > 1:
            if order == 'first_last':
                parts = [u" ".join(parts[1:]), parts[0]]
            else:
                parts = [parts[0], u" ".join(parts[1:])]
        else:
            while len(parts) < 2:
                parts.append(False)
        return {"lastname": parts[0], "firstname": parts[1]}

    @api.model
    def split_name(self, name):
        clean_name = u" ".join(name.split(None)) if name else name
        return self._get_inverse_name(clean_name)

    @api.model
    def _update_employee_names(self):
        employees = self.search([
            ('firstname', '=', ' '), ('lastname', '=', ' ')])

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

    @api.model
    def _names_order_default(self):
        return 'last_first'

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        order = self.env['ir.config_parameter'].get_param(
            'employee_names_order', self._names_order_default())
        return order

    @api.model
    def _get_computed_name(self, lastname, firstname):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        if order == 'last_first_comma':
            return u", ".join((p for p in (lastname, firstname) if p))
        elif order == 'first_last':
            return u" ".join((p for p in (firstname, lastname) if p))
        else:
            return u" ".join((p for p in (lastname, firstname) if p))

    @api.model
    def _get_name(self, lastname, firstname):
        return self._get_computed_name(lastname, firstname)

    @api.multi
    @api.onchange('firstname', 'lastname')
    def get_name(self):
        for employee in self:
            if employee.firstname and employee.lastname:
                employee.name = self._get_name(
                    employee.lastname, employee.firstname)

    def _firstname_default(self):
        return ' ' if self.env.context.get('module') else False

    firstname = fields.Char(
        "Firstname", default=_firstname_default)
    lastname = fields.Char(
        "Lastname", required=True, default=_firstname_default)

    @api.model
    def create(self, vals):
        if vals.get('firstname') and vals.get('lastname'):
            vals['name'] = self._get_name(vals['lastname'], vals['firstname'])

        elif vals.get('name'):
            vals['lastname'] = self.split_name(vals['name'])['lastname']
            vals['firstname'] = self.split_name(vals['name'])['firstname']
        res = super(HrEmployee, self).create(vals)
        self._update_partner_firstname(res)
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
        res = super(HrEmployee, self).write(vals)
        if set(vals).intersection(UPDATE_PARTNER_FIELDS):
            self._update_partner_firstname(self)
        return res
