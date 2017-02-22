# -*- coding: utf-8 -*-
# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    skype_id = fields.Char(
        string='Skype ID',
    )
    twitter_id = fields.Char(
        string='Twitter ID',
    )
    whatsapp_id = fields.Char(
        string='Whatsapp ID',
    )
