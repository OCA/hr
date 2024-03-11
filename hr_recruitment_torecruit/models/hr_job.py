from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    @api.depends("no_of_recruitment")
    def _compute_to_recruit(self):
        contract_obj = self.env["hr.contract"]
        for rec in self:
            rec.to_recruit = rec.no_of_recruitment - contract_obj.search_count(
                [("job_id", "=", rec.id), ("state", "=", "open")]
            )
            if rec.to_recruit > 0:
                rec.website_published = True
            else:
                rec.website_published = False

    to_recruit = fields.Integer(
        string="To be recruited", compute="_compute_to_recruit", store=True
    )
