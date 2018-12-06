# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""
        INSERT INTO hr_employee_skill
            (create_uid, create_date, write_uid, write_date, employee_id,
             skill_id, level)
        SELECT
            1, now() at time zone 'UTC', 1, now() at time zone 'UTC',
            employee_id, skill_id, 0
        FROM
            skill_employee_rel
     """)
