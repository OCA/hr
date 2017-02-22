# -*- coding: utf-8 -*-
# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    birth_name = fields.Char(
        string='Birth Name',
    )
