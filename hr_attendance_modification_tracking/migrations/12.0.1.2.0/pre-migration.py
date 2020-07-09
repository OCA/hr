# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, """
            ALTER TABLE hr_attendance
            ADD COLUMN IF NOT EXISTS time_changed_manually BOOLEAN
        """
    )
