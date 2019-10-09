# -*- coding: utf-8 -*-
# Author: Simone Orsi
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api
import logging

logger = logging.getLogger('[hr_employee_address_improved.post_init_hook]')


def post_init_hook(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners_count = env['res.partner'].search_count([])
    empls = env['hr.employee'].with_context(
        active_test=False).search([('address_home_id', '!=', False)])
    empls.mapped('address_home_id').with_context(
        tracking_disable=True).write({'active': False})
    logger.info(
        'Set all partners assigned to `employee.address_home_id` '
        'as not active. Partners matching: %d out of %d',
        len(empls), partners_count
    )
