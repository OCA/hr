# -*- coding: utf-8 -*-
# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrSocialMedia(models.Model):
    _name = 'hr.social.media'

    name = fields.Char(
        string='Name',
    )
    social_url = fields.Char(
        string='Website',
    )


class HrSocialMediaAccount(models.Model):
    _name = 'hr.social.media.account'

    hr_social_media_id = fields.Many2one(
        'hr.social.media',
        string='Social Media',
        required=True,
    )
    account_name = fields.Char(
        string='Account',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
