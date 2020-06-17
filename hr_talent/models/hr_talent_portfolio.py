# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrTalentPortfolio(models.Model):
    _name = 'hr.talent.portfolio'
    _description = 'HR Talent Portfolio'
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
    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Html(
        string='Description',
        required=True,
    )
    skill_ids = fields.Many2many(
        string='Skills',
        comodel_name='hr.skill',
    )
    url = fields.Char(
        string='URL',
    )
