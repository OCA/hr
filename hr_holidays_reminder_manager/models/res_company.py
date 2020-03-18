from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    PERIODS = [
        (1, "One day"),
        (2, "Two days"),
        (3, "Three days"),
        (7, "One week"),
        (14, "Two weeks"),
    ]

    leave_reminder_period = fields.Selection(
        PERIODS, string="Period before notifying the HR manager", default=1,
    )
