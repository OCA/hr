# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrExperience(models.Model):
    _name = 'hr.experience'
    _inherit = 'hr.curriculum'

    category = fields.Selection([('professional', 'Professional'),
                                 ('academic', 'Academic'),
                                 ('certification', 'Certification')],
                                'Category',
                                required=True,
                                default='professional',
                                help='Category')
