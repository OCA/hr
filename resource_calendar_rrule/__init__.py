# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api
from . import models


def post_init_hook(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for attendance in env['resource.calendar.attendance'].search([]):
        rrule = attendance._default_rrule()
        vals = attendance.read(['date_from', 'date_to', 'dayofweek'])[0]
        attendance._adapt_start_until_from_vals(rrule[0], vals)
        attendance.write({'rrule': rrule})
