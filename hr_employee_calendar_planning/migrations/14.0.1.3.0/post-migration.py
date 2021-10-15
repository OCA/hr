# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["hr.employee"].with_context(active_test=False).search([]).filtered(
        lambda x: any(c.calendar_id.two_weeks_calendar for c in x.calendar_ids)
        and any(not c.calendar_id.two_weeks_calendar for c in x.calendar_ids)
    ).regenerate_calendar()
