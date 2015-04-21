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


def pre_init_hook(cr):
    adjust_employee_partners_pre(cr)


def adjust_employee_partners_pre(cr):
    # point all employees without address_id to a company partner to satisfy
    # newly introduced non null constraint
    cr.execute('update hr_employee e set address_id=c.partner_id '
               'from res_company c where e.address_id is null')


def post_init_hook(cr, pool):
    env = Environment(cr, SUPERUSER_ID, {})
    adjust_employee_partners_post(env)


def adjust_employee_partners_post(env):
    companies = env['res.company'].with_context(active_test=False).search([])
    company_partners = companies.mapped('partner_id')
    for employee in env['hr.employee'].with_context(active_test=False).search(
            [('address_id', 'in', company_partners.ids)]):
        if employee.user_id:
            employee.address_id = employee.user_id.partner_id
        else:
            employee.address_id = env['res.partner'].create({
                'employee': True,
                'name': employee.name,
                'phone': employee.work_phone,
                'email': employee.work_email,
                'mobile': employee.mobile_phone,
                'image': employee.image,
                'active': employee.active,
            })
