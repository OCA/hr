from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    hr_half_day_cancels_voucher = fields.Boolean(
        string="Half working days cancel luncheon vouchers"
    )
