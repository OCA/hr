# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    leave_notify_manager = fields.Boolean(
        related='company_id.leave_notify_manager', readonly=False,
        string="Leave Requests notified to employee's manager",
        help="When a leave request is created the employee's manager "
             "will be added as follower and notified by email.")
