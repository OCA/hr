import logging

from odoo.fields import Command

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Migrate calendars from versions to calendar_ids
    to have consistent work schedule history"""
    employees = env["hr.employee"].with_context(active_test=False).search([])

    for employee in employees.filtered(
        lambda e: e.version_ids.filtered("contract_date_start")
    ):
        version_calendar_lines = []
        versions = employee.version_ids.filtered("contract_date_start").sorted(
            "date_start"
        )
        for version in versions:
            date_start = version.date_start
            date_end = version.date_end
            # filter calendar_ids to check for overlaps with versions
            # with the same work schedule
            cal_ids = employee.calendar_ids.filtered(
                lambda x, version=version: x.calendar_id == version.resource_calendar_id
                and (
                    not x.date_start
                    or not version.date_end
                    or x.date_start < version.date_end
                )
                and (
                    not x.date_end
                    or not version.date_start
                    or x.date_end > version.date_start
                )
            )
            if cal_ids:
                _logger.info(f"{version} is overlapping with {cal_ids}")
                for calendar in cal_ids.sorted("date_start"):
                    if date_start and calendar.date_start != date_start:
                        _logger.info(
                            f"changing date_start of {calendar} "
                            f"from {calendar.date_start} to {date_start}"
                        )
                        calendar.date_start = date_start
                    if date_end and calendar.date_end != date_end:
                        _logger.info(
                            f"changing date_end of {calendar} "
                            f"from {calendar.date_end} to {date_end}"
                        )
                        calendar.date_end = date_end
                    break
            else:
                _logger.info(
                    f"adding new calendar_id for {version.employee_id.name}: "
                    f"{version.resource_calendar_id.name} "
                    f"from {date_start} to {date_end}"
                )
                version_calendar_lines.append(
                    Command.create(
                        {
                            "date_start": date_start,
                            "date_end": date_end,
                            "calendar_id": version.resource_calendar_id.id,
                        }
                    )
                )

        employee.calendar_ids = version_calendar_lines

        # set correct calendar in current version
        # Prevent the resource calendar of leaves to be updated by a write
        employee.version_id.with_context(no_leave_resource_calendar_update=True).update(
            {"resource_calendar_id": employee.resource_calendar_id.id}
        )
