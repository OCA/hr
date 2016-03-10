# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class hr_academic(models.Model):
    _name = 'hr.academic'
    _inherit = 'hr.curriculum'

    diploma = fields.Char(string='Diploma', translate=True)
    study_field = fields.Char(string='Field of study', translate=True,)
    activities = fields.Text(string='Activities and associations',
                             translate=True)
