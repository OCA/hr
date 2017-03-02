# -*- coding: utf-8 -*-
# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    social_media_account_ids = fields.One2many(
        'hr.social.media.account',
        'employee_id',
        string='Social Media Accounts',
    )
