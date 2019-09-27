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
from datetime import date


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    start_date = str(date.today().replace(year=2018, month=1, day=1))
    # Chose this day because its one of the date of execution of the CRON
    end_date = str(date.today().replace(year=2019, month=5, day=24))
    cr.execute("SELECT id FROM hr_employee")
    employees = cr.dictfetchall()
    # Add row for temporary balance
    cr.execute("ALTER TABLE hr_employee "
               "ADD COLUMN  temp_balance double precision")
    for employee in employees:

        balance, lost = employee.past_balance_computation(start_date, end_date, 0)
        # Set temporary balance
        cr.execute("UPDATE hr_employee SET temp_balance = %s "
                   "WHERE id = %s",
                   (balance, employee['id']))
