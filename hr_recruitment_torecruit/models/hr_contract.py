from odoo import api, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.onchange("state")
    def _onchange_state(self):
        self.job_id._compute_to_recruit()
