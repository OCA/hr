# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    department_id = fields.Many2one(
        'hr.department'
    )
