# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _is_employee_contact(self):
        """Check if the partner is related to an employee as work contact.

        Returns:
            bool: True if the partner is linked to an employee via work_contact_id.
        """
        self.ensure_one()
        return bool(self.sudo().employee_ids)

    def _check_can_view_bank_accounts(self):
        """Check if the current user can view bank accounts in this partner.

        Only users with accounting_full_access (group_account_user or
        group_account_manager) can view bank accounts in contacts
        related to employees. Regular contacts show bank accounts to all users.

        Returns:
            bool: True if the user can view bank accounts for this partner.
        """
        self.ensure_one()
        if not self._is_employee_contact():
            return True
        return self.env.user.has_groups(
            "account.group_account_user,account.group_account_manager"
        )

    can_view_bank_accounts = fields.Boolean(
        compute="_compute_can_view_bank_accounts",
        store=False,
        compute_sudo=True,
    )

    @api.depends_context("uid")
    def _compute_can_view_bank_accounts(self):
        """Compute the can_view_bank_accounts field for partners."""
        for partner in self:
            partner.can_view_bank_accounts = partner._check_can_view_bank_accounts()
