# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Quentin Gigon <gigon.quentin@gmail.com>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  previous_period_lost_hours")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  penultimate_period_lost_hours")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  penultimate_period_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  previous_period_continuous_cap")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  previous_annual_balance")
    # cr.execute("ALTER TABLE hr_employee "
    #            "DROP COLUMN  previous_period_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  last_update_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  last_update_date")
