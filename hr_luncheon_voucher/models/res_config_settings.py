from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_half_day_cancels_voucher = fields.Boolean(
        string="Half working days cancel luncheon vouchers",
        related="company_id.hr_half_day_cancels_voucher",
        readonly=False,
    )
