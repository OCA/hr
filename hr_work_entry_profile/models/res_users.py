from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_open_work_entries(self):
        self.ensure_one()
        return self.employee_id.action_open_work_entries()