from psycopg2 import IntegrityError

from odoo import Command, api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # Employee portal users may use in-Odoo notifications, so the stock
    # "share users must use email" check is relaxed to only validate the
    # value itself; the share/employee combination is enforced by
    # _check_employee_notification_type below.
    _notification_type = models.Constraint(
        "CHECK (notification_type IN ('email', 'inbox'))",
        "Invalid notification type",
    )

    @api.depends("share", "all_group_ids", "employee_ids")
    def _compute_notification_type(self):
        # Share users linked to an employee default to in-Odoo notifications:
        # they can't open Discuss, so this mutes their notification emails.
        # It is only a default — an explicit write persists (see the
        # inverse). Internal users keep their own preference.
        employee_users = self.filtered(lambda user: user.share and user.employee_ids)
        employee_users.notification_type = "inbox"
        return super(ResUsers, self - employee_users)._compute_notification_type()

    def _inverse_notification_type(self):
        # Share users never join the inbox notification group: membership is
        # meaningless for them (portal users can't open Discuss), and linking
        # the group would make later 'email' writes snap back to 'inbox'
        # through the group_ids compute dependency. The unlink still runs:
        # an internal user converted to portal relies on it to drop the
        # group, as core Odoo expects (mail's
        # test_notification_type_convert_internal_inbox_to_portal).
        share_users = self.filtered("share")
        if share_users:
            inbox_group = self.env.ref("mail.group_mail_notification_type_inbox")
            share_users.write({"group_ids": [Command.unlink(inbox_group.id)]})
        return super(ResUsers, self - share_users)._inverse_notification_type()

    @api.constrains("share", "employee_ids", "notification_type")
    def _check_employee_notification_type(self):
        # Pure portal users can't use 'inbox' — employee-linked portal
        # users can. Core Odoo's SQL check enforced the share restriction
        # directly; it had to be relaxed to let employees in, so this
        # Python check re-enforces it. IntegrityError matches the stock
        # exception type, keeping upstream tests (mail's
        # test_notification_type_constraint) green.
        for user in self:
            if (
                user.share
                and not user.employee_ids
                and user.notification_type == "inbox"
            ):
                raise IntegrityError(
                    self.env._(
                        "Only internal users and employees can receive"
                        " notifications in Odoo."
                    )
                )
