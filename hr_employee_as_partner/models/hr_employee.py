from odoo import _, fields, models
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    partner_id = fields.Many2one(
        "res.partner",
        "Associated Partner",
        groups="hr.group_hr_user",
        help="Partner that represent the employee",
    )

    def action_create_associated_employee(self):
        self.ensure_one()
        if self.partner_id:
            raise UserError(_("The employee already has a partner associated."))

        context = {
            "default_name": self.name,
            "default_email": self.work_email,
            "default_phone": self.work_phone,
            "default_mobile": self.mobile_phone,
            "default_company_id": self.company_id.id,
            "default_hr_employee_id": self.id,
        }

        return {
            "name": "Associated Partner",
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def _create_associated_employee(self):
        self.ensure_one()
        if self.partner_id:
            raise UserError(_("The employee already has a partner associated."))
        return self.env["res.partner"].create(
            {
                "name": self.name,
                "email": self.work_email,
                "phone": self.work_phone,
                "mobile": self.mobile_phone,
                "company_id": self.company_id.id,
                "hr_employee_id": self.id,
            }
        )

    def _create_all_associated_employees(self):
        for rec in self:
            if not rec.partner_id:
                rec._create_associated_employee()

        return self
