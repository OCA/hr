import logging
from odoo import _
from odoo import fields, models, api


_logger = logging.getLogger(__name__)

class HrAppraisalWizard(models.TransientModel):
    _name = 'hr.appraisal.wizard'
    _inherit = 'mail.thread'
    _description = 'Wizard for feedback visibility confirmation to manager'

    res_model = fields.Char(string='HR Appraisal', required=True)
    res_id = fields.Integer(string='Resource ID', required=True)

    def ok_button(self):
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id)
        record.employee_feedback_published = True
        user_name = self.env.user.name
         # Añadir un registro al tracking
        record.message_post(
            body=_("{user_name} decided, as Appraisal Officer, to publish the employee's feedback").format(user_name=user_name),
            subtype_xmlid="mail.mt_note"
        )

class HrAppraisalRequestWizard(models.TransientModel):
    _name = 'hr.appraisal.request.wizard'
    _inherit = 'mail.composer.mixin'
    _description = 'Request an Appraisal'

    appraisal_id = fields.Many2one('hr.appraisal.employee', required=True)
    recipient_ids = fields.Many2many('res.partner', string='Recipients', required=True)
    user_body = fields.Html(string='User Contents')
    subject= fields.Char(string='Subject')
    recipient_users = fields.Many2many('res.users', string='Recipients Users', store=False)

    @api.model
    def default_get(self, fields):
        res = super(HrAppraisalRequestWizard, self).default_get(fields)

        if self.env.context.get('default_appraisal_id'):
            appraisal = self.env['hr.appraisal.employee'].browse(self.env.context['default_appraisal_id'])
            recipients_ids = self._get_recipients_ids(appraisal)
            recipients_users =  self._get_user_ids(appraisal)

            # Si el usuario actual es un empleado en la ficha (perfil manager o empleado)
            if appraisal.env.user.employee_id == appraisal.employee_id:
                template = self.env.ref('hr_appraisal.mail_template_appraisal_request_from_employee', False)
            else:
                template = self.env.ref('hr_appraisal.mail_template_appraisal_request', False)

            # Obtener el asunto de la plantilla
            subject= self.env['mail.template']._render_template(
                template.subject, template.model, [self.id]
                )[self.id]

            res.update({
                'recipient_ids': recipients_ids.ids,
                'recipient_users': recipients_users.ids if recipients_users else None,
                'subject': subject,
                'appraisal_id': appraisal.id,
            })
        return res

    def _get_user_ids(self, appraisal):
        user_ids = []

        appraisal = self.env['hr.appraisal.employee'].browse(self.env.context['default_appraisal_id'])

        # Si el usuario actual es un empleado en la ficha (perfil manager o empleado)
        if appraisal.env.user.employee_id == appraisal.employee_id:
            # Añadir el usuario de los manager_ids
            for manager in appraisal.manager_ids:
                if manager.user_id:
                    user_ids.append(manager.user_id.id)

         # Si el usuario actual es un manager y está en la lista de manager_user_ids, añadimos solo al empleado como usuario
        elif appraisal.is_manager == True and appraisal.env.user in appraisal.manager_user_ids and appraisal.employee_id.user_id:
            # Añadir el usuario del employee_id
            user_ids.append(appraisal.employee_id.user_id.id)
         # Si el usuario actual es un manager pero no está en la lista de manager_user_ids, añadimos a todos como destinatarios
        elif appraisal.is_manager == True  and appraisal.employee_id.user_id:
            # Añadir el usuario del employee_id y de los manager_ids
            user_ids.append(appraisal.employee_id.user_id.id)

            for manager in appraisal.manager_ids:
                if manager.user_id:
                    user_ids.append(manager.user_id.id)

        for_users = [("id", "in", user_ids)]
        users = self.env["res.users"].search(for_users)

        if len(users) > 0:
            return users

    def _get_recipients_ids(self, appraisal):
            mail_employees =[]

            # Si el usuario actual es un empleado en la ficha (perfil manager o empleado)
            if appraisal.env.user.employee_id == appraisal.employee_id:
                 # Añadir el correo electrónico de los manager_ids
                for manager in appraisal.manager_ids:
                    if manager.work_email:
                        mail_employees.append(manager.work_email)
            # Si el usuario actual es un manager y está en la lista de manager_user_ids, añadimos solo al empleado como destinatario
            elif appraisal.is_manager == True and appraisal.env.user in appraisal.manager_user_ids and appraisal.employee_id.work_email:
                 # Añadir el correo electrónico del employee_id
                mail_employees.append(appraisal.employee_id.work_email)
            # Si el usuario actual es un manager pero no está en la lista de manager_user_ids, añadimos a todos como destinatarios
            elif appraisal.is_manager == True  and appraisal.employee_id.work_email:
                mail_employees.append(appraisal.employee_id.work_email)
                # Añadir el correo electrónico de los manager_ids
                for manager in appraisal.manager_ids:
                    if manager.work_email:
                        mail_employees.append(manager.work_email)

            for_email = [("email", "in", mail_employees)]
            partners = self.env["res.partner"].search(for_email)
            if len(partners) > 0:
                return partners

    def send_button(self):

        self.ensure_one()
        appraisal = self.appraisal_id

        # Si el usuario actual es un empleado en la ficha (perfil manager o empleado)
        if appraisal.env.user.employee_id == appraisal.employee_id:
            template = self.env.ref('hr_appraisal.mail_template_appraisal_request_from_employee', False)
        else:
            template = self.env.ref('hr_appraisal.mail_template_appraisal_request', False)

        if template:

            ctx = {
                'default_use_template': bool(template),
                'default_email_layout_xmlid': 'mail.mail_notification_light',
                'force_email': True,
                'mail_notify_author': True,
                'recipient_users': self.recipient_users,
                'user_body': self.user_body,
            }

            message_composer = self.env['mail.compose.message'].with_context(**ctx).create({
                'res_id': self.appraisal_id.id,
                'model': 'hr.appraisal.employee',
                'partner_ids': self.recipient_ids.ids,
                'template_id': template.id if template else False,
                'email_from': self.env.user.email_formatted,
                'composition_mode': 'comment',
            })

            # Simulate the onchange (like trigger in form the view)
            update_values = message_composer._onchange_template_id(template.id, 'comment', 'hr.appraisal.employee', self.appraisal_id.id)['value']
            message_composer.write(update_values)

            if update_values:
                message_composer.write(update_values)

            message_composer.write({
                'subject': self.subject,
                })

            message_composer._action_send_mail()

            message = self.env['mail.message'].search([
                ('model', '=', 'hr.appraisal.employee'),
                ('res_id', '=', self.appraisal_id.id)
                ], order="id desc", limit=1)

            if message:
                message.write({'reply_to': self.env.user.email_formatted})

