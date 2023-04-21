# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    branch_id = fields.Many2one(
        "res.partner",
        help="Indicate the department branch, to ensure that the "
        "employees are assigned correctly",
    )
