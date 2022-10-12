# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    course_expiration_channel_id = fields.Many2one(
        "mail.channel",
        string="Mailing list to alert",
        default=lambda self: self.env.ref(
            "hr_course.mail_channel_course_validity", raise_if_not_found=False
        ),
    )
    course_expiration_alerting_delay = fields.Integer(
        string="Alerting delay before end of validity (days)"
    )
