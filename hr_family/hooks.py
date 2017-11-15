# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID, api


def post_init_hook(cr, dummy):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for status in ['single', 'married', 'widower', 'divorced']:
        env['hr.employee'].with_context(active_test=False).search([
            ('marital', '=', status),
        ]).write({
            'marital_status_id': env.ref(
                'hr_family.%s' % status
            ).id,
        })
