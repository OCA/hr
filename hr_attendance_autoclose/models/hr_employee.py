# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    no_autoclose = fields.Boolean(string='Don\'t Autoclose Attendances')

    @api.multi
    def get_max_hours_per_day(self):
        self.ensure_one()
        return self.company_id.attendance_maximum_hours_per_day
