# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrAcademic(models.Model):
    """Added the details of the academic."""

    _name = 'hr.academic'
    _inherit = 'hr.curriculum'

    diploma = fields.Char('Diploma',
                          translate=True)
    study_field = fields.Char('Field of Study',
                              translate=True)
    activities = fields.Text('Activities and Associations',
                             translate=True)
