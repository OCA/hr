# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields, models


class HrAppraisal(models.Model):
    _name = "hr.appraisal"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "employee_id"
    _description = "Employee Appraisal"
    _order = "state desc, date_close, id desc"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self._default_employee_id(),
        readonly=True,
        states={"1_new": [("readonly", False)]},
        domain="[('id', 'in', employee_domain_ids)]",
    )
    employee_domain_ids = fields.Many2many(
        "hr.employee",
        compute="_compute_employee_domain_ids",
    )
    manager_ids = fields.Many2many(
        "hr.employee",
        "hr_appraisal_managers_rel",
        "hr_appraisal_id",
        compute="_compute_manager_ids",
        inverse="_inverse_manager_ids",
        domain="[('id', '!=', employee_id)]",
        check_company=True,
        required=True,
        store=True,
    )
    date_close = fields.Date(
        string="Appraisal Date",
        required=True,
        help="Closing date of the current appraisal",
    )
    job_id = fields.Many2one(
        "hr.job", string="Job Position", related="employee_id.job_id"
    )
    department_id = fields.Many2one(
        "hr.department", "Department", compute="_compute_department"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="employee_id.company_id",
        store=True,
    )
    appraisal_template_id = fields.Many2one(
        "hr.appraisal.template",
        string="Appraisal Template",
        check_company=True,
    )
    state = fields.Selection(
        [("1_new", "To Confirm"), ("2_pending", "Confirmed"), ("3_done", "Done")],
        string="Status",
        default="1_new",
        index=True,
        required=True,
        tracking=True,
    )
    employee_feedback = fields.Html(
        compute="_compute_employee_feedback", store=True, readonly=False
    )
    manager_feedback = fields.Html(
        compute="_compute_manager_feedback", store=True, readonly=False
    )
    employee_feedback_published = fields.Boolean(default=True, tracking=True)
    manager_feedback_published = fields.Boolean(default=True, tracking=True)
    can_see_employee_publish = fields.Boolean(
        default=False,
        compute="_compute_can_see_employee_manager_publish",
    )
    can_see_manager_publish = fields.Boolean(
        default=False,
        compute="_compute_can_see_employee_manager_publish",
    )
    employee_appraisal_count = fields.Integer(
        string="Appraisal Count", related="employee_id.appraisal_count"
    )
    color = fields.Integer(string="Color Index")
    created_by = fields.Many2one("res.users", default=lambda self: self.env.uid)
    employee_user_id = fields.Many2one(
        "res.users",
        related="employee_id.user_id",
        string="Employee User",
    )
    manager_user_ids = fields.Many2many(
        "res.users",
        string="Manager Users",
        compute="_compute_manager_user",
    )
    is_manager = fields.Boolean(compute="_compute_is_manager")
    activity_ids = fields.One2many("mail.activity", "res_id", "Activities")
    note = fields.Html(
        string="Private Note",
        help="The content of this note is not visible by the Employee.",
    )
    tag_ids = fields.Many2many("hr.appraisal.tag", string="Tags")
    active = fields.Boolean(default=True)
    employee_feedback_template = fields.Html(compute="_compute_feedback_templates")
    manager_feedback_template = fields.Html(compute="_compute_feedback_templates")

    @api.model
    def default_get(self, fields_list):
        """Set default template and initialize feedback fields.

        - If user already provided values, preserve them.
        - If no template is provided, use the default from config.
        - If no feedback is provided, populate from the selected template.
        """
        res = super().default_get(fields_list)
        if not res.get("appraisal_template_id"):
            default_template_id = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("hr_appraisal_oca.default_appraisal_template_id", 0)
            )
            if default_template_id:
                res["appraisal_template_id"] = default_template_id
        return res

    @api.model
    def _default_employee_id(self):
        """
        Return the default employee for the appraisal.

        - None if the user is an HR Officer or has subordinates.
        - Otherwise, the current user's employee.

        :return: Employee ID or False.
        :rtype: int | bool
        """
        employee, subordinates = self._get_current_employee_and_subordinates()
        if not employee or self.env.user.has_group(
            "hr_appraisal_oca.group_appraisal_hr_officer"
        ):
            return False
        if subordinates.filtered(lambda e: e.id != employee.id):
            return False
        return employee.id

    def _get_current_employee_and_subordinates(self):
        """
        Get the current user's employee and their subordinates
        (direct or indirect).

        :return: Tuple (employee, subordinates recordset).
                Employee is None if not found or user is HR Officer.
        :rtype: tuple(hr.employee | None, recordset(hr.employee))
        """
        user = self.env.user
        Employee = self.env["hr.employee"]
        if user.has_group("hr_appraisal_oca.group_appraisal_hr_officer"):
            return None, Employee
        employee = user.employee_ids[:1]
        if not employee:
            return None, Employee
        subordinates = Employee.search([("id", "child_of", employee.id)])
        return employee, subordinates

    @api.depends_context("uid")
    @api.depends("state")
    def _compute_employee_domain_ids(self):
        Employee = self.env["hr.employee"]
        user = self.env.user
        if user.has_group("hr_appraisal_oca.group_appraisal_hr_officer"):
            allowed = Employee.search([])
        else:
            employee, subordinates = self._get_current_employee_and_subordinates()
            if employee:
                ids = subordinates.ids if subordinates else []
                if employee.id not in ids:
                    ids.append(employee.id)
                allowed = Employee.browse(ids)
            else:
                allowed = Employee.browse()
        for rec in self:
            rec.employee_domain_ids = allowed

    @api.depends("employee_id", "manager_ids")
    def _compute_manager_user(self):
        self.manager_user_ids = [(6, 0, self.manager_ids.user_id.ids)]

    @api.depends("appraisal_template_id")
    def _compute_employee_feedback(self):
        for appraisal in self.filtered(lambda a: a.state == "1_new"):
            appraisal.employee_feedback = appraisal.employee_feedback_template

    @api.depends("appraisal_template_id")
    def _compute_manager_feedback(self):
        for appraisal in self.filtered(lambda a: a.state == "1_new"):
            appraisal.manager_feedback = appraisal.manager_feedback_template

    @api.depends("appraisal_template_id")
    def _compute_feedback_templates(self):
        for appraisal in self:
            template = appraisal.appraisal_template_id
            appraisal.employee_feedback_template = (
                template.appraisal_employee_feedback_template
                if appraisal.appraisal_template_id
                else False
            )
            appraisal.manager_feedback_template = (
                template.appraisal_manager_feedback_template
                if appraisal.appraisal_template_id
                else False
            )

    @api.depends("employee_id")
    def _compute_manager_ids(self):
        for record in self:
            if record.employee_id.parent_id:
                record.manager_ids = record.employee_id.parent_id
            else:
                record.manager_ids = False

    def _inverse_manager_ids(self):
        pass

    def write(self, vals):
        close_appraisal = vals.get("state") == "3_done"
        appraisal_activity_ref = None
        if close_appraisal:
            vals["date_close"] = datetime.date.today()
            appraisal_activity_ref = self.env.ref(
                "hr_appraisal_oca.mail_act_hr_appraisal_cfr"
            )
        if close_appraisal and appraisal_activity_ref:
            # Check and mark activities as "done"
            for appraisal in self:
                activities = appraisal.activity_ids.filtered(
                    lambda act: act.activity_type_id == appraisal_activity_ref
                )
                if activities:
                    activities.action_feedback()
        return super().write(vals)

    @api.depends("employee_id")
    def _compute_department(self):
        for appraisal in self:
            if appraisal.employee_id:
                appraisal.department_id = appraisal.employee_id.department_id
            else:
                appraisal.department_id = False

    @api.depends_context("uid")
    @api.depends("state", "employee_id")
    def _compute_is_manager(self):
        """Compute if the current user is a manager for this record."""
        user = self.env.user
        is_hr_officer = user.has_group("hr_appraisal_oca.group_appraisal_hr_officer")
        employee = user.employee_ids[:1]
        is_manager_user = False
        if employee:
            is_manager_user = bool(
                self.env["hr.employee"].search_count([("parent_id", "=", employee.id)])
            )
        for record in self:
            record.is_manager = (
                False
                if record.employee_user_id.id == user.id
                else is_hr_officer or is_manager_user
            )

    def _visibility_role(self, rec, user_emp, uid):
        if user_emp and rec.employee_id == user_emp:
            return "user_employee"
        user_is_assigned_manager = uid in rec.manager_ids.mapped("user_id").ids
        if rec.is_manager and user_is_assigned_manager:
            return "user_manager"
        if rec.is_manager:
            return "record_manager"
        return "other"

    @api.depends_context("uid")
    @api.depends("state", "employee_id", "manager_ids")
    def _compute_can_see_employee_manager_publish(self):
        MAPPING = {
            ("1_new", "user_employee"): (True, False),
            ("1_new", "user_manager"): (True, True),
            ("2_pending", "user_employee"): (True, False),
            ("2_pending", "user_manager"): (False, True),
            ("2_pending", "record_manager"): (True, True),
            ("3_done", "user_employee"): (True, False),
            ("3_done", "user_manager"): (False, True),
            ("3_done", "record_manager"): (False, True),
        }
        user_employee = self.env.user.employee_ids[:1]
        user_id = self.env.user.id
        for rec in self:
            role = self._visibility_role(rec, user_employee, user_id)
            rec.can_see_employee_publish, rec.can_see_manager_publish = MAPPING.get(
                (rec.state, role), (False, False)
            )

    @api.onchange("employee_id", "manager_ids", "state")
    def _onchange_visibility_flags(self):
        # FIXME: review how to execute the method without using this onchange
        # in the context of user = employee without subordinates.
        self._compute_can_see_employee_manager_publish()

    def action_confirm(self):
        """
        Confirm the appraisal by setting its state to 'pending'
        and resetting feedback flags.

        - Sends confirmation emails to the employee and managers.
        - Creates CFR activities for the employee and managers
            if they have associated users.
        """
        self.state = "2_pending"
        self.employee_feedback_published = False
        self.manager_feedback_published = False
        template = "hr_appraisal_oca.mail_template_appraisal_confirmation"
        if self.employee_id.work_email:
            self._send_email(
                self.employee_id.user_id, template, self.employee_id.work_email
            )
        if self.employee_user_id.id:
            user_id = int(self.employee_user_id.id)
            self._create_activity_cfr(user_id)
        for record in self:
            for manager in record.manager_ids:
                if manager.work_email:
                    self._send_email(manager.user_id, template, manager.work_email)
                if manager.user_id.id:
                    user_id = int(manager.user_id.id)
                    self._create_activity_cfr(user_id)

    def action_done(self):
        """
        Mark the appraisal as done, publish feedback flags, send completion emails,
        and log the status change.

        - Sets state to 'done' and marks feedback as published.
        - Sends completion emails to the employee and all managers with valid emails.
        - Posts a message indicating the appraisal was completed by the current user.
        """
        self.state = "3_done"
        self.employee_feedback_published = True
        self.manager_feedback_published = True
        template = "hr_appraisal_oca.mail_template_appraisal_completed"
        if self.employee_id.work_email:
            self._send_email(
                self.employee_id.user_id, template, self.employee_id.work_email
            )
        for record in self:
            for manager in record.manager_ids:
                if manager.work_email:
                    self._send_email(manager.user_id, template, manager.work_email)

    def action_back(self):
        self.state = "1_new"

    def _send_email(self, recipient_users, template, email):
        if not email or not recipient_users:
            return
        ctx = {"recipient_users": recipient_users}
        self.env["send.email.with.template"].send_email_with_template(
            template,
            self.id,
            email,
            ctx,
        )

    def _create_activity_cfr(self, user_id):
        activity_type = (
            self.env.ref(
                "hr_appraisal_oca.mail_act_hr_appraisal_cfr",
                raise_if_not_found=False,
            )
            or self.env["mail.activity.type"]
        )
        if activity_type:
            self.activity_schedule(
                "hr_appraisal_oca.mail_act_hr_appraisal_cfr",
                date_deadline=self.date_close,
                summary=_("Appraisal Form to Fill"),
                note=_(
                    "Fill appraisal for %(employee)s ", employee=self.employee_id.name
                ),
                user_id=user_id,
            )

    def action_open_employee_appraisals(self):
        return {
            "name": _("Previous Appraisals"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "hr.appraisal",
            "domain": [("employee_id", "=", self.employee_id.id)],
            "context": dict(
                self.env.context,
                group_by=["date_close:month"],
                search_default_group_by=False,
            ),
        }

    def action_publish_employee_feedback(self):
        if (
            not self.employee_feedback_published
            and self.employee_id.user_id.id != self.env.user.id
        ):
            view_id = self.env.ref("hr_appraisal_oca.hr_appraisal_wizard_form_view").id
            view_item = [(view_id, "form")]
            return {
                "name": _("Confirmation"),
                "view_type": "form",
                "view_mode": "form",
                "view_id": view_id,
                "res_model": "hr.appraisal.wizard",
                "views": view_item,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "default_res_model": "hr.appraisal",
                    "default_res_id": self.id,
                },
            }
        else:
            self.employee_feedback_published = not self.employee_feedback_published

    def action_publish_manager_feedback(self):
        self.manager_feedback_published = not self.manager_feedback_published

    def action_send_appraisal_request(self):
        if self.employee_id:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "hr.appraisal.request.wizard",
                "target": "new",
                "name": _("Appraisal Request"),
                "context": {"default_appraisal_id": self.id},
            }
