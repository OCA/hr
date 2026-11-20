def post_init_hook(env):
    # The stored compute only re-runs when a dependency changes, so push
    # existing employee portal users through the dependency edge once to
    # land the new 'inbox' default on them.
    env["res.users"].search(
        [("share", "=", True), ("employee_ids", "!=", False)]
    ).modified(["employee_ids"])
    env.flush_all()


def uninstall_hook(env):
    # The models.Constraint redefinition is applied by the ORM on install
    # but is not dropped on uninstall. Reset the rows that would violate
    # the stock check, then restore it so the DB is left in a stock state.
    env.cr.execute(
        "UPDATE res_users SET notification_type='email' "
        "WHERE share AND notification_type='inbox'"
    )
    env.cr.execute(
        "ALTER TABLE res_users DROP CONSTRAINT IF EXISTS res_users_notification_type"
    )
    env.cr.execute(
        "ALTER TABLE res_users ADD CONSTRAINT res_users_notification_type "
        "CHECK (notification_type = 'email' OR NOT share)"
    )
    env.invalidate_all()
