from odoo import fields, models


class MeetingType(models.Model):

    _inherit = "calendar.event.type"

    ref = fields.Char(
        string="Reference",
        copy=False,
        store=True,
    )
    remove_luncheon_voucher = fields.Boolean(
        string="Remove luncheon voucher",
        copy=True,
        store=True,
    )
