# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployeePPE(models.Model):
    """Adds PPE information and allocation."""

    _name = 'hr.employee.ppe'
    _description = 'Personal Protective Equipments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one(
        string='Equipment',
        required=True,
        comodel_name='hr.employee.ppe.equipment',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    start_date = fields.Date(
        'Start Date',
        default=fields.Date.today()
    )
    end_date = fields.Date('End Date')
    description = fields.Text('Description')
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        help="Employer, School, University"
        "Certification Authority"
    )
    location = fields.Char('Location', help="Location")
    expire = fields.Boolean('Expire', help="Expire", default=True)
    certification = fields.Char(
        'Certification Number',
        help='Certification Number'
    )
    status = fields.Selection(
        [('valid', 'Valid'), ('expired', 'Expired')],
        default='valid',
        readonly=True,
        help='Certification Number'
    )

    @api.onchange('name')
    def verify_expiracy(self):
        self.expire = self.name.expirable
