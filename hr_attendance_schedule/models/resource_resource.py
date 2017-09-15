# -*- coding: utf-8 -*-
from odoo import fields, models


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    leave_ids = fields.One2many('resource.calendar.leaves', 'resource_id', "Leaves")
