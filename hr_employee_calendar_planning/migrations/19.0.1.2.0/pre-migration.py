# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo.addons.hr_employee_calendar_planning.hooks import pre_init_hook


@openupgrade.migrate()
def migrate(env, version):
    pre_init_hook(env)
