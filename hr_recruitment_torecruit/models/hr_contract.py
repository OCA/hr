from odoo import models


class HrContract(models.Model):
    _inherit = "hr.contract"

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            job_obj = self.job_id
            job_obj._compute_to_recruit()
        return res
