# -*- coding: utf-8 -*-
from openerp import api, SUPERUSER_ID


def migrate(cr, version):

    def _get_employer(env, empl_name):
        p_model = env['res.partner']
        employer = p_model.search(
            [('is_company', '=', True), ('name', '=', empl_name.strip())]
        )
        return employer and employer[0] or p_model.create(
            {'name': empl_name, 'is_company': True})

    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        ''' select id, fam_spouse_bk, fam_spouse_employer_bk,
        fam_spouse_tel_bk from hr_employee where fam_spouse_bk is not null'''
    )
    for empl_id, spouse_name, spouse_empl, spouse_phone in cr.fetchall():
        spouse = env['res.partner'].create({
            'name': spouse_name,
            'employer': _get_employer(env, spouse_empl).id,
            'phone': spouse_phone,
        })
        env['hr.employee'].browse(empl_id).write(
            {'partner_spouse_id': spouse.id}
        )
    cr.execute(
        '''ALTER TABLE hr_employee DROP COLUMN fam_spouse_bk,
        DROP COLUMN fam_spouse_employer_bk,
        DROP COLUMN fam_spouse_tel_bk'''
    )
