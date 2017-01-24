# -*- coding: utf-8 -*-
# ©  2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

UPDATE_PARTNER_FIELDS = ['firstname', 'lastname', 'user_id', 'address_home_id']


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def split_name(self, name):
        clean_name = u" ".join(name.split(None)) if name else name
        return self.env['res.partner']._get_inverse_name(clean_name)

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
    def _get_name(self, lastname, firstname):
        return self.env['res.partner']._get_computed_name(lastname, firstname)

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
