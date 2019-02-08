# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class HrSocialMedia(models.Model):
    _name = 'hr.social.media'
    _description = 'HR Social Media'

    name = fields.Char(
        required=True,
    )
    social_url = fields.Char(
        string='Website',
    )


class HrSocialMediaAccount(models.Model):
    _name = 'hr.social.media.account'
    _description = 'HR Employee Social Media Account'

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )
    hr_social_media_id = fields.Many2one(
        'hr.social.media',
        string='Social Media',
        required=True,
    )
    account_name = fields.Char(
        string='Account',
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )

    @api.multi
    @api.depends('hr_social_media_id.name', 'account_name')
    def _compute_name(self):
        for social_media_account in self:
            social_media_account.name = _('%s (%s)') % (
                social_media_account.account_name,
                social_media_account.hr_social_media_id.name
            )
