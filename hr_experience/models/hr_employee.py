# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academic_ids = fields.One2many('hr.academic',
                                   'employee_id',
                                   'Academic experiences',
                                   help="Academic experiences")
    certification_ids = fields.One2many('hr.certification',
                                        'employee_id',
                                        'Certifications',
                                        help="Certifications")
    experience_ids = fields.One2many('hr.experience',
                                     'employee_id',
                                     ' Professional Experiences',
                                     help='Professional Experiences')
