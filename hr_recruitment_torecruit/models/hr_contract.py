from odoo import models


class HrContract(models.Model):
    _inherit = "hr.contract"

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            job_obj = self.env["hr.job"].search([("to_recruit", ">", 0)])
            for job in job_obj:
                job._compute_to_recruit()
        return res
