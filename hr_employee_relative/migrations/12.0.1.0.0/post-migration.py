# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    columns = 'fam_spouse, fam_spouse_employer, fam_spouse_tel, fam_father,' \
              ' fam_father_date_of_birth, fam_mother, fam_mother_date_of_birth'
    cr.execute('SELECT id, %s FROM hr_employee' % columns)

    relation_spouse = env.ref('hr_employee_relative.relation_spouse').id
    relation_parent = env.ref('hr_employee_relative.relation_parent').id
    relation_child = env.ref('hr_employee_relative.relation_child').id

    for employee in cr.fetchall():
        if employee[1] or employee[2] or employee[3]:
            env['hr.employee.relative'].create({
                'employee_id': employee[0],
                'job': employee[2],
                'phone_number': employee[3],
                'name': employee[1] or 'Spouse',
                'relation_id': relation_spouse
            })
        if employee[4] or employee[5]:
            env['hr.employee.relative'].create({
                'employee_id': employee[0],
                'name': employee[4] or 'Father',
                'date_of_birth': employee[5] or False,
                'relation_id': relation_parent
            })
        if employee[6] or employee[7]:
            env['hr.employee.relative'].create({
                'employee_id': employee[0],
                'name': employee[6] or 'Mother',
                'date_of_birth': employee[7] or False,
                'relation_id': relation_parent
            })
    cr.execute(
        'SELECT name, date_of_birth, employee_id, gender'
        ' FROM hr_employee_children'
    )
    for children in cr.fetchall():
        env['hr.employee.relative'].create({
            'name': children[0] or 'Child',
            'date_of_birth': children[1] or False,
            'employee_id': children[2],
            'gender': children[3] or False,
            'relation_id': relation_child
        })
