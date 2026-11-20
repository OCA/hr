from odoo import models
from odoo.exceptions import UserError
from odoo.tools import email_normalize


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def action_grant_portal_access(self):
        """Create a portal user for this employee's work contact.

        Reuses the portal.wizard logic for user creation, validation, and
        invitation email, then links the new user to this employee.
        """
        self.ensure_one()
        if self.user_id:
            raise UserError(self.env._("This employee is already linked to a user."))
        partner = self.work_contact_id
        if not partner or len(partner.employee_ids) > 1:
            # Create a dedicated partner for this employee
            self.work_contact_id = False
            self.sudo()._create_work_contacts()
            partner = self.work_contact_id
        if not partner:
            raise UserError(
                self.env._("Could not resolve a personal contact for this employee.")
            )
        email = email_normalize(partner.email or self.work_email)
        if not email:
            raise UserError(
                self.env._("Employee must have a valid email to grant portal access.")
            )
        # Create wizard records and delegate to portal.wizard.user
        wizard = self.env["portal.wizard"].create({})
        wizard_user = self.env["portal.wizard.user"].create(
            {
                "wizard_id": wizard.id,
                "partner_id": partner.id,
                "email": email,
            }
        )
        wizard_user.action_grant_access()
        # Portal users don't count as "grants" on the wizard user row, so the
        # created user is resolved from the partner's user_ids instead.
        partner.invalidate_recordset(["user_ids"])
        user = partner.sudo().with_context(active_test=False).user_ids[:1]
        if user:
            self.sudo().write({"user_id": user.id})
