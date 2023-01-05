from odoo import fields, models


class Contract(models.Model):
    _inherit = "hr.contract"

    leave_ids = fields.One2many("hr.leave", "contract_id", string="Leaves")

    def l10n_no_action_new_leave(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.leave",
            "views": [[False, "form"]],
            "context": "{'default_employee_id': %d,'default_contract_id': %d}"
            % (self.employee_id.id, self.id),
        }
