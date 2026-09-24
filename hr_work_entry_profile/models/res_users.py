# Copyright 2023 Janik von Rotz <janik.vonrotz@mint-system.ch>
# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_open_work_entries(self):
        self.ensure_one()
        return self.employee_id.action_open_work_entries()
