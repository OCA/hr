from datetime import datetime, timedelta
from odoo import api, models, fields


class HRLeave(models.Model):
    _inherit = "hr.leave"

    reminder_id = fields.Many2one(string="Mail", comodel_name="mail.mail",)

    @api.multi
    def _get_hr_managers_to_notify(self):
        """Defines the hr managers to notify."""
        self.ensure_one()
        managers = self.env["hr.employee"].search([["hr_manager", "=", True]])
        return managers

    @api.multi
    def _get_body_mail(self, template):
        view = self.env["ir.ui.view"].browse(
            self.env["ir.model.data"].xmlid_to_res_id(template)
        )
        msg = False
        for record in self:
            model_description = (
                self.env["ir.model"]._get(record._name).display_name
            )
            values = {
                "object": record,
                "model_description": model_description,
            }
            msg = view.render(values, engine="ir.qweb", minimal_qcontext=True)
            msg = self.env["mail.thread"]._replace_local_links(msg)
        return msg

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if self.first_approver_id and self.reminder_id:
            if self.holiday_status_id.double_validation:
                self.reminder_id.send()
            else:
                self.reminder_id.unlink()
            self.reminder_id = False
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._planning_reminder_hr()
        return res

    @api.multi
    def _planning_reminder_hr(self):
        """Input: res.user"""
        self.ensure_one()
        company = self.employee_id.company_id
        managers = self._get_hr_managers_to_notify()
        if not managers:
            return True
        applicant = self.employee_id
        managers_email = [
            manager.user_id.email
            for manager in managers
            if manager.user_id
        ]
        email_to = ", ".join(managers_email)
        mail_values = {
            "auto_delete": True,
            "notification": True,
            "mail_server_id": (
                self.env["ir.mail_server"].sudo().search([], limit=1).id,
            ),
            "model": "hr.leave",
            "res_id": self.id,
            "scheduled_date": (
                datetime.today()
                + timedelta(days=company.leave_reminder_period)
            ),
            "reply_to": applicant.user_id.email,
            "email_to": email_to,
            "email_from": (
                f"From {applicant.name}, <{applicant.user_id.email}>"
            ),
            "subject": f"Reminder leave request - {applicant.name}",
            "body_html": self._get_body_mail(
                template=(
                    "hr_holidays_reminder_manager."
                    "message_reminder_hr_managers"
                ),
            ),
        }
        self.reminder_id = self.env["mail.mail"].create(mail_values)
        return True
