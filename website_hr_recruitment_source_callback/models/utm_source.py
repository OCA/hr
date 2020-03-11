# -*- coding:utf-8 -*-
from odoo import _, fields, models


class UTMSource(models.Model):
    _inherit = "utm.source"

    js_callback_snippet = fields.Text(
        string="Callback Snippet",
        help=_("""Javascript script to perform some action after
        successful application sending"""),
    )
