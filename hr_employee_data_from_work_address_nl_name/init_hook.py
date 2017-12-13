# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
from openerp import SUPERUSER_ID
from openerp.api import Environment


def post_init_hook(cr, pool):
    # we have installed both hr_employee_data_from_work_address that provides
    # us syncing between work address (partner) and l10n_nl_employee_name that
    # provides us the extra NL name fields (firstname, lastname
    # initials, infix) on hr_employee and also res_user through its dependency
    # on l10n_nl_partner_name.
    # Now we sync the values of these fields from res_user to Hr_employee, this
    # module will keep them synced after

    env = Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].with_context(active_test=False).search([])
    company_partners = companies.mapped('partner_id')
    env['hr.employee']._model._register_hook(env.cr)
    employees = env['hr.employee'].with_context(active_test=False).search(
        [('address_id', 'in', company_partners.ids)], order='id')
    env.cr.execute('select firstname, lastname, initials, infix from
                   res_partners where id in %s order by id',
                   (tuple(employees.ids),))
    employee_data = env.cr.fetchall()
    # we make a first write on employee of the NL NAME data in it's address_id
    # the module will then keep it synced
    for employee, data in zip(employees, employee_db_data):
        employee.address_id.write({
            'firstname' : data['firstname'],
            'lastname' : data['lastname'],
            'initials' : data['initials'],
            'infix' : data['infix'],
        })
