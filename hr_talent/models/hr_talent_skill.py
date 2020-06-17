# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrTalentSkill(models.Model):
    _name = 'hr.talent.skill'
    _description = 'HR Talent Skill'
    _rec_name = 'complete_name'
    _order = 'sequence, experience desc, id'

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
    skill_id = fields.Many2one(
        string='Skill',
        comodel_name='hr.skill',
        ondelete='restrict',
        required=True,
    )
    highlight = fields.Boolean(
        string='Highlight',
    )
    experience = fields.Integer(
        string='Years of Experience',
        index=True,
    )
    last_used = fields.Integer(
        string='Last Used (year)',
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    _sql_constraints = [
        (
            'hr_talent_skill_uniq',
            'UNIQUE(talent_id, skill_id)',
            'Same skill can be specified only once for a talent!'
        ),
    ]

    @api.multi
    @api.depends('skill_id.name', 'experience')
    def _compute_complete_name(self):
        for talent_skill in self:
            talent_skill.complete_name = _(
                '%(skill)s (%(experience)s years)'
            ) % {
                'skill': talent_skill.skill_id.name,
                'experience': talent_skill.experience,
            }
