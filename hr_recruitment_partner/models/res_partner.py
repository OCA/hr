# -*- coding: utf-8 -*-
# Copyright (C) 2018 Daniel Reis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'
    is_applicant = fields.Boolean('Is Applicant?')
