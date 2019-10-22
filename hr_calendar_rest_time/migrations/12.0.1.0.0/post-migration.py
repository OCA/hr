# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    calendars = env['resource.calendar'].search([])
    for calendar in calendars:
        calendar._onchange_hours_per_day()
