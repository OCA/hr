# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class HrAppraisalWizard(models.TransientModel):
    _name = "hr.appraisal.wizard"
    _inherit = "mail.thread"
    _description = "Wizard for feedback visibility confirmation to manager"

    res_model = fields.Char(string="HR Appraisal", required=True)
    res_id = fields.Integer(string="Resource ID", required=True)

    def ok_button(self):
        """Publish employee feedback as manager."""
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id)
        record.employee_feedback_published = True
        message = _(
            "{user_name} decided, as Appraisal Officer, "
            "to publish the employee's feedback"
        ).format(user_name=self.env.user.name)
        record.message_post(
            body=message,
            subtype_xmlid="mail.mt_note",
        )


class HrAppraisalRequestWizard(models.TransientModel):
    _name = "hr.appraisal.request.wizard"
    _inherit = "mail.composer.mixin"
    _description = "Request an Appraisal"

    appraisal_id = fields.Many2one("hr.appraisal", required=True)
    recipient_ids = fields.Many2many("res.partner", string="Recipients", required=True)
    user_body = fields.Html(string="User Contents")
    subject = fields.Char()
    recipient_users = fields.Many2many(
        "res.users", string="Recipients Users", store=False
    )

    @api.model
    def default_get(self, fields):
        """
        Provide default values based on 'default_appraisal_id' in context.

        Prefills recipients, users, subject, and appraisal ID using related
        appraisal and appropriate email template.
        """
        res = super().default_get(fields)
        appraisal_id = self.env.context.get("default_appraisal_id")
        if not appraisal_id:
            return res
        appraisal = self.env["hr.appraisal"].browse(appraisal_id)
        recipients_ids = self._get_appraisal_recipients(appraisal, field="work_email")
        recipients_users = self._get_appraisal_recipients(appraisal, field="user_id")
        template_xml_id = (
            "hr_appraisal_oca.mail_template_appraisal_request_from_employee"
            if appraisal.env.user.employee_id == appraisal.employee_id
            else "hr_appraisal_oca.mail_template_appraisal_request"
        )
        template = self.env.ref(template_xml_id, False)
        subject = self.env["mail.template"]._render_template(
            template.subject, template.model, [self.id]
        )[self.id]
        res.update(
            {
                "recipient_ids": recipients_ids.ids,
                "recipient_users": recipients_users.ids or None,
                "subject": subject,
                "appraisal_id": appraisal.id,
            }
        )
        return res

    def _get_appraisal_recipients(self, appraisal, field="user_id"):
        """
        Get recipients related to the appraisal for notifications.

        :param appraisal: hr.appraisal record
        :param field: Field to extract ('user_id' or 'work_email')
        :return: res.users or res.partner recordset
        """
        values = []
        if appraisal.env.user.employee_id == appraisal.employee_id:
            # Employee: notify managers
            for manager in appraisal.manager_ids:
                value = getattr(manager, field)
                if value:
                    values.append(value.id if field == "user_id" else value)
        elif (
            appraisal.is_manager
            and appraisal.env.user in appraisal.manager_user_ids
            and getattr(appraisal.employee_id, field)
        ):
            # Manager listed: notify employee
            value = getattr(appraisal.employee_id, field)
            values.append(value.id if field == "user_id" else value)
        elif appraisal.is_manager and getattr(appraisal.employee_id, field):
            # Other managers: notify employee and managers
            value = getattr(appraisal.employee_id, field)
            values.append(value.id if field == "user_id" else value)
            for manager in appraisal.manager_ids:
                value = getattr(manager, field)
                if value:
                    values.append(value.id if field == "user_id" else value)
        if field == "user_id":
            return self.env["res.users"].search([("id", "in", values)])
        return self.env["res.partner"].search([("email", "in", values)])

    def send_button(self):
        """Send appraisal request email using the appropriate template."""
        self.ensure_one()
        appraisal = self.appraisal_id
        template_xml_id = (
            "hr_appraisal_oca.mail_template_appraisal_request_from_employee"
            if appraisal.env.user.employee_id == appraisal.employee_id
            else "hr_appraisal_oca.mail_template_appraisal_request"
        )
        template = self.env.ref(template_xml_id, False)
        if not template:
            return
        ctx = {
            "default_use_template": True,
            "default_email_layout_xmlid": "mail.mail_notification_light",
            "force_email": True,
            "mail_notify_author": True,
            "recipient_users": self.recipient_users,
            "user_body": self.user_body,
        }
        composer = (
            self.env["mail.compose.message"]
            .with_context(**ctx)
            .create(
                {
                    "res_id": appraisal.id,
                    "model": "hr.appraisal",
                    "partner_ids": self.recipient_ids.ids,
                    "template_id": template.id,
                    "email_from": self.env.user.email_formatted,
                    "composition_mode": "comment",
                }
            )
        )
        update_values = composer._onchange_template_id(
            template.id, "comment", "hr.appraisal", appraisal.id
        ).get("value", {})
        if update_values:
            composer.write(update_values)
        composer.write({"subject": self.subject})
        composer._action_send_mail()
        message = self.env["mail.message"].search(
            [("model", "=", "hr.appraisal"), ("res_id", "=", appraisal.id)],
            order="id desc",
            limit=1,
        )
        if message:
            message.write({"reply_to": self.env.user.email_formatted})
