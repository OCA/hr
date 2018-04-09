# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrCertification(models.Model):
    _name = 'hr.certification'
    _inherit = 'hr.curriculum'

    certification = fields.Char('Certification Number',
                                help='Certification Number')
