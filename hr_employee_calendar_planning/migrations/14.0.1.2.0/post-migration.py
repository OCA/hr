# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if version >= "14.0.1.0.0":
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE resource_calendar
            SET auto_generate = true
            WHERE active = false""",
        )
