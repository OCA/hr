# Copyright 2018-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    include_in_theoretical = fields.Boolean(
        string="Include in theoretical hours",
        help="If you check this mark, leaves in this category won't reduce "
             "the number of theoretical hours in the attendance report.",
    )
