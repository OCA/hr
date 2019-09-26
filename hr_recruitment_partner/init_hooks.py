# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Daniel Reis
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
###############################################################################

from openerp import SUPERUSER_ID
from openerp.api import Environment


def pre_init_hook(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    env.cr.execute(
        'UPDATE hr_applicant SET partner_id=1 WHERE partner_id IS NULL')


def post_init_hook(cr, pool):
    env = Environment(cr, SUPERUSER_ID, {})
    # create a new partner for all applicants with no real partner assigned
    applicants = env['hr.applicant'].with_context(active_test=False).\
        search([('partner_id', '=', 1)], order='id')
    # we need to read related values from the database because the related
    # fields already cover our fields
    if not applicants:
        return
    env.cr.execute(
        'select id, name, partner_name, '
        'partner_phone, partner_mobile, email_from '
        'from hr_applicant where id in %s order by id',
        (tuple(applicants.ids),))
    applicant_data = env.cr.dictfetchall()
    for applicant, db_data in zip(applicants, applicant_data):
        applicant.partner_id = env['res.partner'].create({
            'name': applicant.partner_name or applicant.name,
            'phone': db_data['partner_phone'],
            'mobile': db_data['partner_mobile'],
            'email': db_data['email_from'],
            'customer': False,
        })
