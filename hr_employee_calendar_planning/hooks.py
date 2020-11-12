# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry, employees=None):
    """Split current calendars by date ranges and assign new ones for
    having proper initial data.
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        if not employees:
            employees = env["hr.employee"].search([])
        calendars = employees.mapped("resource_calendar_id")
        calendar_obj = env["resource.calendar"]
        line_obj = env["resource.calendar.attendance"]
        groups = line_obj.read_group(
            [("calendar_id", "in", calendars.ids)],
            ["calendar_id", "date_from", "date_to"],
            ["calendar_id", "date_from:day", "date_to:day"],
            lazy=False,
        )
        calendar_mapping = defaultdict(list)
        for group in groups:
            calendar = calendar_obj.browse(group["calendar_id"][0])
            lines = line_obj.search(group["__domain"])
            if len(calendar.attendance_ids) == len(lines):
                # Don't alter calendar, as it's the same
                new_calendar = calendar
            else:
                name = calendar.name + " {}-{}".format(
                    lines[0].date_from,
                    lines[0].date_to,
                )
                attendances = []
                for line in lines:
                    data = line.copy_data({"date_from": False, "date_to": False})[0]
                    data.pop("calendar_id")
                    attendances.append((0, 0, data))
                new_calendar = calendar_obj.create(
                    {"name": name, "attendance_ids": attendances}
                )
            calendar_mapping[calendar].append(
                (lines[0].date_from, lines[0].date_to, new_calendar),
            )
        for employee in employees.filtered("resource_calendar_id"):
            calendar_lines = []
            for data in calendar_mapping[employee.resource_calendar_id]:
                calendar_lines.append(
                    (
                        0,
                        0,
                        {
                            "date_start": data[0],
                            "date_end": data[1],
                            "calendar_id": data[2].id,
                        },
                    )
                )
            # Extract employee's existing leaves so they are passed to the new
            # automatic calendar.
            leaves = employee.resource_calendar_id.leave_ids.filtered(
                lambda x: x.resource_id == employee.resource_id
            )
            employee.calendar_ids = calendar_lines
            employee.resource_calendar_id.active = False
            # Now the automatic calendar has been created, so we link the
            # leaves to that one so they count correctly.
            leaves.write({"calendar_id": employee.resource_calendar_id.id})
