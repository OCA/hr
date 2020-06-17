# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrTalentEmployment(models.Model):
    _name = 'hr.talent.employment'
    _description = 'HR Talent Employment'
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
    company = fields.Char(
        string='Company',
        required=True,
    )
    position = fields.Char(
        string='Position',
        required=True,
    )
    start_year = fields.Integer(
        string='Start of Employment (year)',
        required=True,
    )
    end_year = fields.Integer(
        string='End of Employment (year)',
    )
    skill_ids = fields.Many2many(
        string='Skills',
        comodel_name='hr.skill',
    )
    accomplishments = fields.Html(
        string='Accomplishments',
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    @api.multi
    @api.depends('position', 'company', 'start_year', 'end_year')
    def _compute_complete_name(self):
        for talent_employment in self:
            if talent_employment.end_year:
                talent_employment.complete_name = _(
                    '%(position)s at %(institution)s (%(start)s - %(end)s'
                    ')'
                ) % {
                    'position': talent_employment.position,
                    'company': talent_employment.company,
                    'start': talent_employment.start_year,
                    'end': talent_employment.end_year,
                }
            else:
                talent_employment.complete_name = _(
                    '%(position)s at %(institution)s (%(start)s - Present)'
                ) % {
                    'position': talent_employment.position,
                    'company': talent_employment.company,
                    'start': talent_employment.start_year,
                }
