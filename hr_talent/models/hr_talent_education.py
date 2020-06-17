# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrTalentEducation(models.Model):
    _name = 'hr.talent.education'
    _description = 'HR Talent Education'
    _rec_name = 'complete_name'
    _order = 'sequence, id'

    active = fields.Boolean(
        default=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        index=True,
        default=10,
    )
    talent_id = fields.Many2one(
        string='Talent',
        comodel_name='hr.talent',
        ondelete='cascade',
        required=True,
    )
    degree = fields.Char(
        string='Degree',
        required=True,
    )
    institution = fields.Char(
        string='Institution',
        required=True,
    )
    location = fields.Char(
        string='Location',
        required=True,
    )
    field_of_study = fields.Char(
        string='Field of Study',
        required=True,
    )
    admission_year = fields.Integer(
        string='Year of Admission',
        required=True,
    )
    graduation_year = fields.Integer(
        string='Year of Graduation',
        required=True,
    )
    skill_ids = fields.Many2many(
        string='Skills',
        comodel_name='hr.skill',
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    @api.multi
    @api.depends('degree', 'institution', 'admission_year', 'graduation_year')
    def _compute_complete_name(self):
        for talent_education in self:
            talent_education.complete_name = _(
                '%(degree)s at %(institution)s (%(admission)s - %(graduation)s'
                ')'
            ) % {
                'skill': talent_education.degree,
                'institution': talent_education.institution,
                'admission': talent_education.admission_year,
                'graduation': talent_education.graduation_year,
            }
