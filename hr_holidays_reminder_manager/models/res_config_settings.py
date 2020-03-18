from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    PERIODS = [
        (1, "One day"),
        (2, "Two days"),
        (3, "Three days"),
        (7, "One week"),
        (14, "Two weeks"),
    ]

    leave_reminder_period = fields.Selection(
        PERIODS,
        related="company_id.leave_reminder_period",
        readonly=False,
        string="Period before notifying the HR manager",
        default=1,
    )
