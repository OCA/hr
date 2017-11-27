# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        'alter table hr_employee rename column fam_spouse to fam_spouse_bk'
    )
    cr.execute(
        'alter table hr_employee rename column fam_spouse_employer to '
        'fam_spouse_employer_bk'
    )
    cr.execute(
        'alter table hr_employee rename column fam_spouse_tel to '
        'fam_spouse_tel_bk'
    )
