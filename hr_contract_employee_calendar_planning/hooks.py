import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry, employees=None):
    """Migrate calendars from contracts to calendar_ids
    to have consistent work schedule history"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not employees:
        employees = env["hr.employee"].with_context(active_test=False).search([])

    for employee in employees.filtered("contract_ids"):
        contract_calendar_lines = []
        for contract in employee.contract_ids.sorted("date_start"):
            date_start = contract.date_start
            date_end = contract.date_end
            # filter calendar_ids to check for overlaps with contracts
            # with the same work schedule
            cal_ids = employee.calendar_ids.filtered(
                lambda x: x.calendar_id == contract.resource_calendar_id
                and (not x.date_start or not date_end or x.date_start < date_end)
                and (not x.date_end or not date_start or x.date_end > date_start)
            )
            if cal_ids:
                _logger.info(f"{contract} is overlapping with {cal_ids}")
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
                    f"adding new calendar_id for {contract.employee_id.name}: "
                    f"{contract.resource_calendar_id.name} from {date_start} to {date_end}"
                )
                contract_calendar_lines.append(
                    (
                        0,
                        0,
                        {
                            "date_start": date_start,
                            "date_end": date_end,
                            "calendar_id": contract.resource_calendar_id.id,
                        },
                    )
                )

        employee.calendar_ids = contract_calendar_lines

        # set correct calendar in contract
        employee.contract_id.resource_calendar_id = employee.resource_calendar_id
