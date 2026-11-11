- Portal users cannot open the Discuss app, so "In Odoo" notifications are
  effectively silent for them — they produce `mail.notification` records
  that nobody reads, instead of emails. This is intentional: the goal is to
  stop notification emails for employees using only the portal.
- This module relies on `res.users.notification_type`. If Odoo ever removes
  that field (an announced intent, repeatedly postponed), the fallback
  design is intercepting `mail.thread._notify_get_recipients` to drop or
  coerce employee-linked partners — the same outcome without relying on
  the field.
