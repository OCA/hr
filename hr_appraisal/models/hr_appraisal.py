import logging
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HrAppraisal(models.Model):
    _name = 'hr.appraisal.employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _description = 'HR Appraisal'
    _order = 'state desc, date_close, id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self._default_employee_id(),  readonly=True, states={"1_new": [("readonly", False)]})
    manager_ids = fields.Many2many('hr.employee', 'hr_appraisal_manager_rel', 'hr_appraisal_employee_id',
        domain="[('id', '!=', employee_id), ('active', '=', 'True'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True)

    date_close = fields.Date(string='Appraisal Date', required=True, help="Closing date of the current appraisal")
    job_id = fields.Many2one('hr.job', string='Job Position', related="employee_id.job_id", readonly=True)
    department_id = fields.Many2one('hr.department', "Department", compute='_compute_department', readonly=True)

    company_id  = fields.Many2one('res.company', string='Company', related='employee_id.company_id', store=True, readonly=True)
    appraisal_template_id = fields.Many2one('hr.appraisal.employee.template', string='Appraisal Template', store=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", compute='_compute_default_appraisal_template')

    state = fields.Selection([
            ('1_new', 'To Confirm'),
            ('2_pending', 'Confirmed'),
            ('3_done', 'Done')
        ], string='Status', default='1_new', index=True, store=True, required=True, tracking=True)

    employee_feedback = fields.Html(string="Employee Feedback", compute="_compute_feedback_templates", store=True)
    manager_feedback = fields.Html(string="Manager Feedback", compute="_compute_feedback_templates", store=True)

    employee_feedback_published = fields.Boolean(string="Employee Feedback Published", default=True, tracking=True)
    manager_feedback_published = fields.Boolean(string="Manager Feedback Published", default=True, tracking=True)

    can_see_employee_publish = fields.Boolean(default=False, compute='_compute_can_see_employee_manager_publish', readonly=True)
    can_see_manager_publish = fields.Boolean(default=False, compute='_compute_can_see_employee_manager_publish', readonly=True)

    employee_appraisal_count = fields.Integer(string="Appraisal Count", related='employee_id.appraisal_count', readonly=True)

    # for coloring the kanban box
    color = fields.Integer(string="Color Index")
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.uid)

    employee_user_id = fields.Many2one('res.users', related='employee_id.user_id', string='Employee User', readonly=True)
    manager_user_ids = fields.Many2many('res.users', string='Manager Users', readonly=True, compute='_compute_manager_user')

    is_manager = fields.Boolean(string="Is Manager", compute='_compute_is_manager', readonly=True)
    activity_ids = fields.One2many('mail.activity', 'res_id', 'Activities', store=True)
    last_appraisal_id = fields.Many2one('hr.appraisal.employee', related='employee_id.last_appraisal_id')
    note = fields.Html(string="Private Note", help="The content of this note is not visible by the Employee.")

    @api.model
    def _default_employee_id(self):
        user = self.env.user
        # Si el usuario no pertenece el grupo de manager de evaluación, entonces se obtiene el empleado asociado al usuario
        if not user.has_group('hr_appraisal.group_appraisal_manager'):
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            return employee.id if employee else False
        return False

    @api.depends('employee_id')
    def _compute_default_appraisal_template(self):
        # Lógica para obtener la plantilla por defecto
        if self.employee_id and not self.appraisal_template_id:
            default_template = self.env['hr.appraisal.employee.template'].search([('is_default', '=', True)], limit=1)
            if default_template:
                self.appraisal_template_id = default_template.id
            else:
                self.appraisal_template_id = False

    @api.depends_context('uid')
    @api.depends('employee_id', 'manager_ids')
    def _compute_manager_user(self):
        # Lógica para calcular manager_user_ids
        user_ids = []
        for manager in self.manager_ids:
            if manager.user_id:
                user_ids.append(manager.user_id.id) # Añadir el ID del usuario manager
        self.manager_user_ids = [(6, 0, user_ids)]

    @api.depends('appraisal_template_id')
    def _compute_feedback_templates(self):
        for appraisal in self:
            if appraisal.appraisal_template_id:
                appraisal.employee_feedback = appraisal.appraisal_template_id.appraisal_employee_feedback_template
                appraisal.manager_feedback = appraisal.appraisal_template_id.appraisal_manager_feedback_template

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
       # Lógica para calcular manager_ids
        if self.employee_id.parent_id:
            self.manager_ids = [(6, 0, [self.employee_id.parent_id.id])]
        else:
            self.manager_ids = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        record = super(HrAppraisal, self).create(vals)
        if 'employee_feedback' in vals:
            record.employee_feedback = vals["employee_feedback"] # Actualizar el valor de employee_feedback
        if 'manager_feedback' in vals:
            record.manager_feedback = vals["manager_feedback"] # Actualizar el valor de manager_feedback
        if vals.get('state') and vals['state'] == '1_new':
            record.employee_id.sudo().write({
                    'last_appraisal_id': record.id,
                    })
        return record

    def write(self, vals):
        if 'state' in vals and vals['state'] in ['2_pending', '3_done']:
            for appraisal in self:
                appraisal.employee_id.sudo().write({
                    'last_appraisal_id': appraisal.id})
        if 'state' in vals and vals['state'] == '3_done':
            vals['date_close'] = datetime.date.today()
            # Verificar y marcar actividades como "hechas"
            for appraisal in self:
                activities = appraisal.activity_ids.filtered(
                    lambda act: act.activity_type_id.id == self.env.ref('hr_appraisal.mail_act_hr_appraisal_employee_cfr').id
                )
                if activities:
                    activities.action_feedback()  # Marca las actividades como "hechas"

        res = super(HrAppraisal, self).write(vals)
        return res

    @api.depends('employee_id')
    def _compute_department(self):
        for appraisal in self:
            if appraisal.employee_id:
                appraisal.department_id = appraisal.employee_id.department_id
            else:
                appraisal.department_id = False

    @api.depends('state')
    @api.depends_context('uid')
    def _compute_is_manager(self):
        for record in self:
            record.is_manager = self.env.user.has_group('hr_appraisal.group_appraisal_manager')

    @api.depends('state', 'manager_ids')
    def _compute_can_see_employee_manager_publish(self):
        for record in self:
            # _logger.info("_compute_can_see_employee_manager_publish: %s", self.state)
            if self.state == '1_new':
                if self.is_manager and self.env.user.id in self.manager_ids.mapped('user_id').ids:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = True

                elif self.env.user.employee_id == record.employee_id:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = False

                elif record.is_manager:
                    record.can_see_employee_publish = False
                    record.can_see_manager_publish = False

                # Lanza un error si el usuario no es gerente y el empleado no coincide con el usuario
                elif not record.is_manager and record.employee_id.user_id != self.env.user.id:
                    raise UserError(_("You can't change employees because you're not a manager and "
                                      "the employee doesn't match you."))

            elif self.state == '2_pending':
                if self.is_manager and self.env.user.id in self.manager_ids.mapped('user_id').ids:
                    record.can_see_employee_publish = False
                    record.can_see_manager_publish = True

                elif self.env.user.employee_id == record.employee_id:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = False

                elif record.is_manager:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = True

            elif self.state == '3_done':
                if self.env.user.employee_id == record.employee_id:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = False

                elif record.is_manager:
                    record.can_see_employee_publish = True
                    record.can_see_manager_publish = True

    def action_confirm(self):
        self.state = '2_pending'
        self.employee_feedback_published = False
        self.manager_feedback_published = False

        # Envío el email de confirmación al empleado
        if self.employee_id.work_email:
            self._send_confirmation_email(self.employee_id.user_id, self.employee_id.work_email)

        # Creamos la actividad para el empleado si tiene usuario
        if self.employee_user_id.id:
            user_id = int(self.employee_user_id.id)
            self._create_activity_CFR(user_id)

        for record in self:

            for manager in record.manager_ids:
                #Envío el email de confirmación a los managers
                if manager.work_email:
                    self._send_confirmation_email(manager.user_id, manager.work_email)

                # Crear actividad para el manager si tiene usuario
                if manager.user_id.id:

                    user_id = int(manager.user_id.id)
                    self._create_activity_CFR(user_id)


    def action_done(self):
        self.state = '3_done'
        self.employee_feedback_published = True
        self.manager_feedback_published = True

        # Envío el email de finalización al empleado
        if self.employee_id.work_email:
            self._send_completed_email(self.employee_id.user_id, self.employee_id.work_email)

        for record in self:

            for manager in record.manager_ids:
                #Envío el email de finalización a los managers
                if manager.work_email:
                    self._send_completed_email(manager.user_id, manager.work_email)

        # Añadir un registro al tracking
        self.message_post(
            body = _("The appraisal's status has been set to Done by {user_name}").format(user_name=self.env.user.name),
            subtype_xmlid="mail.mt_note"
        )

    def action_back(self):
        self.state = '1_new'

    def _send_confirmation_email(self, recipient_users, email):

        # Lógica para enviar un correo electrónico de confirmación al empleado y otro al manager
        if email:

            ctx = {
                'recipient_users': recipient_users
            }

            self.env['send.email.with.template'].send_email_with_template(
                'hr_appraisal.mail_template_appraisal_confirmation',
                self.id,
                email,
                ctx
            )
            # Desvincular el mensaje del chatter después de enviarlo
            message = self.env['mail.message'].search([
                ('model', '=', 'hr.appraisal.employee'),
                ('res_id', '=', self.id)
            ], order="id desc", limit=1)

            if message:
                message.write({'model': False, 'res_id': False})  # Desvincular del chatter sin eliminarlo

    def _send_completed_email(self, recipient_users, email):

            # Lógica para enviar un correo electrónico de finalización al empleado y otro al manager
            if email:

                ctx = {
                'recipient_users': recipient_users
                }

                self.env['send.email.with.template'].send_email_with_template(
                    'hr_appraisal.mail_template_appraisal_completed',
                    self.id,
                    email,
                    ctx
                )
                # Desvincular el mensaje del chatter después de enviarlo

                # Obtener el ID del tipo de actividad con el xml_id "mail_act_hr_appraisal_employee_cfr"
                activity_type_id = self.env.ref('hr_appraisal.mail_act_hr_appraisal_employee_cfr').id

                # Obtener el ID del subtipo "Activities" (en_US o es_ES)
                subtype_activities = self.env['mail.message.subtype'].search([
                                        ('name', 'in', ['Activities', 'Actividades'])
                                    ], limit=1)

                message = self.env['mail.message'].search([
                    ('model', '=', 'hr.appraisal.employee'),
                    ('res_id', '=', self.id),
                    ('mail_activity_type_id', '!=', activity_type_id), # Excluir el tipo de actividad específico
                    ('subtype_id', '!=', subtype_activities.id),  # Excluir el subtipo "Activities"
                ], order="id desc", limit=1)

                if message:
                    message.write({'model': False, 'res_id': False})

    def _create_activity_CFR(self, user_id):
        # Crea un nuevo registro en el modelo 'mail.activity' para cada manager con usuario
        activity_type = self.env.ref('hr_appraisal.mail_act_hr_appraisal_employee_cfr', raise_if_not_found=False) or self.env['mail.activity.type']

        if activity_type:
            self.activity_schedule('hr_appraisal.mail_act_hr_appraisal_employee_cfr',
                                    date_deadline= self.date_close,
                                    summary= _('Appraisal Form to Fill'),
                                    note= _('Fill appraisal for %(employee)s ', employee=self.employee_id.name),
                                    user_id=user_id)

    def action_open_employee_appraisals(self):
        return {
            'name': _('Previous Appraisals'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hr.appraisal.employee',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': dict(self.env.context, group_by=['date_close:month'], search_default_group_by=False),
        }

    def action_publish_employee_feedback(self):
        if not self.employee_feedback_published and self.is_manager:
            view_item = [(self.env.ref('hr_appraisal.hr_appraisal_wizard_form_view').id, 'form')]
            view = self.env.ref('hr_appraisal.hr_appraisal_wizard_form_view')
            return {
            'name': _('Confirmation'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'hr.appraisal.wizard',
            'views': view_item,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': 'hr.appraisal.employee',
                'default_res_id': self.id,
            },
        }
        else:
            self.employee_feedback_published = not self.employee_feedback_published

    def action_publish_manager_feedback(self):
        self.manager_feedback_published = not self.manager_feedback_published


    def action_send_appraisal_request(self):
        if self.employee_id:
            return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.appraisal.request.wizard',
            'target': 'new',
            'name': _('Appraisal Request'),
            'context': {'default_appraisal_id': self.id},
            }

class SendEmailWithTemplate(models.TransientModel):

    _name = 'send.email.with.template'
    _description = 'Sending Email with Template'

    @api.model
    def send_email_with_template(self, template_xml_id, recipient_id, email, ctx):
        # Get the email template
        template = self.env.ref(template_xml_id)

        if not template:
            raise ValueError(_("Template with XML ID {template_xml_id} not found.").format(template_xml_id=template_xml_id))

        # Send email to a specific record
        template.with_context(lang=self.env.user.lang, **ctx).send_mail(
            recipient_id,  # ID of the record to send email to
            force_send=True,
            raise_exception=False,
            email_layout_xmlid="mail.mail_notification_light",
            email_values={'email_to': email ,'reply_to': self.env.user.email_formatted},
        )
        return True

