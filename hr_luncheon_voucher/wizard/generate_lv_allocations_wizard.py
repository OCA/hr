from odoo import fields, models


class GenerateLVAllocationRequests(models.TransientModel):
    _name = "generate.lv.allocation.requests"
    _description = "Generate Luncheon Vouchers Allocations Requests"
    distrib_campaign_name = fields.Char("Distribution campaign", required=True)
    date_from = fields.Datetime(string="Start Date", required=True)
    date_to = fields.Datetime(string="End Date", required=True)

    def generate_lv_allocations(self):
        values = {}
        values["distrib_campaign_name"] = self.distrib_campaign_name
        values["date_from"] = self.date_from
        values["date_to"] = self.date_to
        employees = self.env["hr.employee"].search(
            [
                ("id", "in", self.env.context.get("active_ids")),
            ]
        )
        employees.generate_mass_lv_allocation(values)
        # Open lv allocation tree view
        return self.env["ir.actions.act_window"]._for_xml_id(
            "hr-luncheon-voucher.act_lv_allocations"
        )
