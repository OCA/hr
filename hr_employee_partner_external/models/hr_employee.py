# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EmployeePartner(models.Model):
    """
    Add administrative Partner reference to Employee
    """

    _inherit = "hr.employee"

    # set employee as external
    is_external = fields.Boolean(
        "Is an external Employee", default=False, groups="hr.group_hr_user",
    )
    # Partner reference
    hr_external_partner_id = fields.Many2one(
        "res.partner",
        "External Partner",
        groups="hr.group_hr_user",
        help="Partner that administrate Employee that works in the Company",
    )
