# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE resource_calendar
        ADD COLUMN IF NOT EXISTS stored_flexible_hours BOOL
        """,
    )
    env.cr.execute(
        """
        ALTER TABLE resource_calendar
        ADD COLUMN IF NOT EXISTS stored_full_time_required_hours double precision
        """,
    )
    env.cr.execute(
        """
        ALTER TABLE resource_calendar
        ADD COLUMN IF NOT EXISTS stored_hours_per_day double precision
        """,
    )
    env.cr.execute(
        """
        UPDATE resource_calendar
        SET stored_flexible_hours = flexible_hours,
            stored_full_time_required_hours = full_time_required_hours,
            stored_hours_per_day = hours_per_day
        """,
    )
