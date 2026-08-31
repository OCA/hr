# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command


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


def post_init_hook(env, employees=None):
    """Set the appropriate calendar for employees who do not yet have one."""
    employee_model = env["hr.employee"].with_context(active_test=False)
    if not employees:
        employees = employee_model.search([])
    employees = employee_model.search(
        [("id", "in", employees.ids), ("calendar_ids", "=", False)]
    )
    for employee in employees:
        leaves = employee.version_ids.resource_calendar_id.leave_ids.filtered(
            lambda x, e=employee: x.resource_id == e.resource_id
        )
        calendar_data = [
            Command.create(
                {
                    "date_start": version.date_start,
                    "date_end": version.date_end,
                    "calendar_id": version.resource_calendar_id.id,
                }
            )
            for version in employee.version_ids
        ]
        employee.write({"calendar_ids": calendar_data})
        employee.copy_global_leaves()
        # Now the automatic calendar has been created, so we link the
        # leaves to that one so they count correctly.
        leaves.write({"calendar_id": employee.resource_calendar_id.id})
