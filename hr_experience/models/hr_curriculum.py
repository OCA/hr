# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrCurriculum(models.Model):
    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"

    name = fields.Char('Name', required=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Employer, School, University, "
                                      "Certification Authority")
    location = fields.Char('Location', help="Location")
    expire = fields.Boolean('Expire', help="Expire", default=True)
