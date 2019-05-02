# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Nicolas Badoux <n.badoux@hotmail.com>
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

    # compute extra hours lost until last cron execution
    last_computation = str(date.today().year) + '-01-01'
    cr.execute("SELECT id FROM hr_employee")
    employees = cr.dictfetchall()
    cr.execute("ALTER TABLE hr_employee "
               "ADD COLUMN  yearly_hours_lost double precision")
    for employee in employees:
        cr.execute("""
            SELECT
                SUM(extra_hours_lost) AS previous_hours_lost
            FROM 
                hr_attendance_day
            WHERE
                employee_id = %s AND date < %s
        """, (employee["id"], last_computation))
        previous_extra_hours_lost = cr.dictfetchone()["previous_hours_lost"]
        cr.execute("UPDATE hr_employee SET yearly_hours_lost = %s "
                   "WHERE id = %s",
                   (previous_extra_hours_lost, employee['id']))
