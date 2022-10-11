from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    lv_allocations_ids = fields.One2many("hr.lv.allocation", "employee_id")

    total_acquired_lv = fields.Integer(
        string="Total allocated luncheon vouchers", store=True, copy=False
    )
    distributed_lv = fields.Integer(
        string="Distributed luncheon vouchers", store=True, copy=False
    )
    dued_lv = fields.Integer(
        string="Remaining luncheon vouchers", store=True, copy=False
    )

    default_monthly_lv = fields.Integer(
        string="Default monthly distribution", store=True, copy=True
    )

    def refresh_lv_values(self):
        for record in self:
            record._compute_total_acquired_lv()
            record._compute_distributed_lv()
            record._compute_dued_lv()

    def _compute_total_acquired_lv(self):
        for record in self:
            allocations = self.env["hr.lv.allocation"].search(
                [
                    ("employee_id", "=", record.id),
                    ("state", "=", ["confirmed", "distributed"]),
                ]
            )
            record.total_acquired_lv = sum(allocations.mapped("number_acquired_lv"))

    def _compute_distributed_lv(self):
        for record in self:
            allocations = self.env["hr.lv.allocation"].search(
                [("employee_id", "=", record.id), ("state", "=", "distributed")]
            )
            record.distributed_lv = sum(allocations.mapped("number_distributed_lv"))

    def _compute_dued_lv(self):
        for record in self:
            record.dued_lv = record.total_acquired_lv - record.distributed_lv

    def generate_mass_lv_allocation(self, values):
        for record in self:
            record.generate_lv_allocation(values)

    def generate_lv_allocation(self, values):
        self.ensure_one()
        values["employee_id"] = self.id
        values["name"] = values["distrib_campaign_name"] + " - " + self.name
        self.env["hr.lv.allocation"].create(values)

    def action_lv_allocations(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr-luncheon-voucher.act_lv_allocations"
        )
        action["context"] = {
            "search_default_employee_id": self.id,
            "default_employee_id": self.id,
        }
        action["domain"] = [("employee_id", "=", self.id)]
        return action

    def action_lv_allocations_requests_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr-luncheon-voucher.lv_allocations_requests_wizard_action"
        )
        ctx = dict(self.env.context)
        ctx["active_ids"] = self.ids
        action["context"] = ctx
        return action
