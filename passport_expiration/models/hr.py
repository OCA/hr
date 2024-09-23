# Copyright 2013 Savoir-faire Linux
# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    passport_expiration_date = fields.Date(
        "Expiration Date",
        help="Expiration date of the passport.",
        groups="hr.group_hr_user",
    )
