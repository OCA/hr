# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrTalentCertification(models.Model):
    _name = 'hr.talent.certification'
    _description = 'HR Talent Certification'
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
    subject = fields.Char(
        string='Subject',
        required=True,
    )
    issuer = fields.Char(
        string='Issuer',
        required=True,
    )
    issue_date = fields.Date(
        string='Issued On',
        required=True,
    )
    expiration_date = fields.Date(
        string='Expires On',
    )
    serial_number = fields.Char(
        string='Serial No.',
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
    @api.depends('subject', 'issuer')
    def _compute_complete_name(self):
        for talent_certification in self:
            talent_certification.complete_name = _(
                '%(subject)s by %(issuer)s'
            ) % {
                'subject': talent_certification.subject,
                'issuer': talent_certification.issuer,
            }
