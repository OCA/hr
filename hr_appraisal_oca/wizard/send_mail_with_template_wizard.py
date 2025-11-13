from odoo import _, api, models


class SendEmailWithTemplate(models.TransientModel):
    _name = "send.email.with.template"
    _description = "Sending Email with Template"

    @api.model
    def send_email_with_template(self, template_xml_id, recipient_id, email, ctx):
        template = self.env.ref(template_xml_id)
        if not template:
            raise ValueError(
                _("Template with XML ID {template_xml_id} not found.").format(
                    template_xml_id=template_xml_id
                )
            )
        template = template.with_context(**ctx)
        subject = template._render_field("subject", [recipient_id], post_process=False)[
            recipient_id
        ]
        body = template._render_field("body_html", [recipient_id], post_process=True)[
            recipient_id
        ]
        mail_values = {
            "email_from": self.env.user.email_formatted,
            "author_id": self.env.user.partner_id.id,
            "model": None,
            "res_id": None,
            "subject": subject,
            "body_html": body,
            "auto_delete": True,
            "email_to": email,
            "reply_to": self.env.user.email_formatted,
        }
        template_ctx = {
            "model_description": self.env["ir.model"]._get("hr.appraisal").display_name,
            "message": self.env["mail.message"]
            .sudo()
            .new(dict(body=mail_values["body_html"], record_name=_("Appraisal"))),
            "company": self.env.company,
        }
        body = self.env["ir.qweb"]._render(
            "mail.mail_notification_light",
            template_ctx,
            minimal_qcontext=True,
            raise_if_not_found=False,
        )
        if body:
            mail_values["body_html"] = self.env[
                "mail.render.mixin"
            ]._replace_local_links(body)
        self.env["mail.mail"].sudo().create(mail_values)
