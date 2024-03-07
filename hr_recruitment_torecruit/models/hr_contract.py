from odoo import api, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.onchange("state")
    def _onchange_state(self):
        job_obj = self.env["hr.job"].search([("to_recruit", ">", 0)])
        for job in job_obj:
            job._compute_to_recruit()
