# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Regularize the period value to morning."""
    openupgrade.logged_query(
        env.cr,
        """UPDATE resource_calendar_attendance
        SET day_period = 'morning'
        WHERE day_period = 'all_day'""",
    )
