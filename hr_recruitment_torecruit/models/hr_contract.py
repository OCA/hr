from odoo import models


class HrContract(models.Model):
    _inherit = "hr.contract"

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            job_obj = self.job_id.filtered(lambda j: j.to_recruit > 0)
            job_obj._compute_to_recruit()
        return res
