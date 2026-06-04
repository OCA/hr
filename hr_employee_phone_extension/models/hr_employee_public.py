# copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    internal_number = fields.Char(related="employee_id.internal_number", readonly=True)
    short_number = fields.Char(related="employee_id.short_number", readonly=True)
