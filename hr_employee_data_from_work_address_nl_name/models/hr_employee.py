# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    firstname = fields.Char(related=['address_id', 'firstname'], store=False)
    lastname = fields.Char(related=['address_id', 'lastname'], store=False)
    initials = fields.Char(related=['address_id', 'initials'], store=False)
    infix = fields.Char(related=['address_id', 'infix'], store=False)

    # onchange_company, onchange_address_id, _reassign_user_id_partner 
    # in the module hr_employee_data_from_work_address work for this 
    # module too. I copy _register_hook for this module fields too.

    def _register_hook(self, cr):
        for field in ['firstname', 'lastname', 'initials', 'infix']:
            if field in self._columns:
                self._columns[field].store = False
                self._fields[field].column = self._columns[field]
            self._fields[field].store = False
            self.pool._store_function[self._name] = [
                spec
                for spec in self.pool._store_function[self._name]
                if spec[1] != field
            ]
