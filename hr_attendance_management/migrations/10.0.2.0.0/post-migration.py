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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    for att_day in env['hr.attendance.day'].search([]):
        balance = att_day.balance_computation()
        cr.execute("""
            UPDATE hr_attendance_day
            SET day_balance = {}
            WHERE id = {}
        """.format(balance, att_day.id))
    employees = env['hr.employee'].search([])
    employees.write({
        'extra_hours_continuous_cap': True,
        'previous_period_continuous_cap': True,
        'penultimate_period_balance': 0,
        'penultimate_period_lost_hours': 0,
    })
    employees._compute_balance()
    for employee in employees:
        cr.execute("""
            SELECT yearly_hours_lost FROM hr_employee WHERE id=%s
        """, (employee.id,))
        employee.previous_period_lost_hours =\
            cr.dictfetchone()['yearly_hours_lost']

    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN  yearly_hours_lost")
    # The previous for loop set the employee.balance to zero. After multiple
    # hours of debugging, we were not able to find the root cause of the bug.
    # Calling _compute_balance again is a work around.
    employees._compute_balance()



