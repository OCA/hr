# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_sheet_range = fields.Selection(
        related="company_id.attendance_sheet_range",
        string="Attendance Sheet Range",
        help="The range of your Attendance Sheet.",
        readonly=False,
    )

    attendance_week_start = fields.Selection(
        related="company_id.attendance_week_start",
        string="Week Starting Day",
        help="Starting day for Attendance Sheets.",
        readonly=False,
    )

    attendance_sheet_review_policy = fields.Selection(
        related="company_id.attendance_sheet_review_policy", readonly=False
    )

    auto_lunch = fields.Boolean(
        string="Auto Lunch",
        related="company_id.auto_lunch",
        help="Forces a lunch period if duration is over the max time.",
        readonly=False,
    )

    auto_lunch_duration = fields.Float(
        string="Duration",
        related="company_id.auto_lunch_duration",
        help="The duration on an attendance that would trigger an auto lunch.",
        readonly=False,
    )

    auto_lunch_hours = fields.Float(
        string="Lunch Hours",
        related="company_id.auto_lunch_hours",
        help="Enter the lunch period that would be used for an auto lunch.",
        readonly=False,
    )
