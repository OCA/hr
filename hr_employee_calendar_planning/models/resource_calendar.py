# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    active = fields.Boolean(
        default=True,
    )
