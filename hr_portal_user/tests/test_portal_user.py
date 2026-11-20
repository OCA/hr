from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from odoo.addons.mail.tests.common import mail_new_test_user


@tagged("post_install", "-at_install")
class TestEmployeePortalUser(TransactionCase):
    """Portal users for employees and their notification preference."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Portal Employee", "work_email": "employee@example.com"}
        )

    def _new_portal_user(self, login):
        return mail_new_test_user(
            self.env,
            login=login,
            name=login,
            email=f"{login}@example.com",
            groups="base.group_portal",
        )

    def test_grant_portal_access(self):
        """Granting portal access creates and links a portal user."""
        self.assertFalse(self.employee.user_id)
        self.employee.action_grant_portal_access()
        user = self.employee.user_id
        self.assertTrue(user)
        self.assertTrue(user.share)
        # A second call is refused: the employee already has a user
        with self.assertRaises(UserError):
            self.employee.action_grant_portal_access()

    def test_portal_employee_defaults_to_inbox(self):
        """Linking a portal user to an employee defaults it to In Odoo."""
        user = self._new_portal_user("portal_employee")
        self.assertEqual(user.notification_type, "email")
        self.employee.user_id = user
        self.assertEqual(user.notification_type, "inbox")
        # The inbox preference is virtual: no inbox-group membership
        inbox_group = self.env.ref("mail.group_mail_notification_type_inbox")
        self.assertNotIn(inbox_group, user.group_ids)

    def test_portal_employee_notification_editable(self):
        """The In Odoo default can be edited back to By Emails."""
        user = self._new_portal_user("portal_employee_edit")
        self.employee.user_id = user
        self.assertEqual(user.notification_type, "inbox")
        user.notification_type = "email"
        self.assertEqual(user.notification_type, "email")
        # Round trip both ways must not snap back
        user.notification_type = "inbox"
        self.assertEqual(user.notification_type, "inbox")
        user.notification_type = "email"
        self.assertEqual(user.notification_type, "email")

    def test_pure_portal_user_cannot_notify_in_odoo(self):
        """A portal user without employee cannot be set to In Odoo."""
        user = self._new_portal_user("pure_portal")
        with self.assertRaises(IntegrityError):
            user.notification_type = "inbox"

    def test_notification_type_constraint_upstream(self):
        """Replicates mail's test_notification_type_constraint.

        Guards against this module silently changing the contract that the
        upstream test asserts: a pure portal user cannot be created with
        in-Odoo notifications.
        """
        with self.assertRaises(IntegrityError):
            mail_new_test_user(
                self.env,
                login="portal_inbox_create",
                name="Portal Inbox Create",
                email="portal_inbox_create@example.com",
                notification_type="inbox",
                groups="base.group_portal",
            )

    def test_internal_to_portal_conversion_unchanged(self):
        """An internal inbox user converted to portal still gets email."""
        user = mail_new_test_user(
            self.env,
            login="internal_to_portal",
            name="Internal To Portal",
            email="internal_to_portal@example.com",
            notification_type="inbox",
            groups="base.group_user",
        )
        self.assertEqual(user.notification_type, "inbox")
        inbox_group = self.env.ref("mail.group_mail_notification_type_inbox")
        self.assertIn(inbox_group, user.group_ids)

        user.write(
            {
                "group_ids": [
                    (3, self.env.ref("base.group_user").id),
                    (4, self.env.ref("base.group_portal").id),
                ]
            }
        )
        self.assertEqual(user.notification_type, "email")
        self.assertNotIn(inbox_group, user.group_ids)

    def test_unlink_employee_falls_back_to_email(self):
        """Unlinking the employee returns the portal user to email."""
        user = self._new_portal_user("portal_employee_unlink")
        self.employee.user_id = user
        self.assertEqual(user.notification_type, "inbox")
        self.employee.user_id = False
        self.assertEqual(user.notification_type, "email")

    def test_employee_portal_search_filter(self):
        """The Employee Portal filter matches only employee portal users."""
        employee_portal = self._new_portal_user("filter_employee")
        self.employee.user_id = employee_portal
        pure_portal = self._new_portal_user("filter_pure_portal")

        found = self.env["res.users"].search(
            [("share", "=", True), ("employee_ids", "!=", False)]
        )
        self.assertIn(employee_portal, found)
        self.assertNotIn(pure_portal, found)
        self.assertNotIn(self.env.user, found)
