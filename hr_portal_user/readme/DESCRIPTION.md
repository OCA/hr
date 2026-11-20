Grant a portal user to an employee, directly from the employee form,
and allow for employees to not receive email notifications.

Portal users linked to an employee default to the "In Odoo" notification
preference instead of "By Emails". Since portal users cannot open the
backend Discuss app, this effectively mutes the notification emails they
would otherwise receive (chatter messages, assignments, document shares).

The notification preference stays editable: an administrator can switch an
employee portal user back to "By Emails" on the user form, where the
preference is also made visible for employee portal users.

Portal users without a linked employee are unaffected and keep the stock
"By Emails" behavior; they still cannot be set to "In Odoo".
