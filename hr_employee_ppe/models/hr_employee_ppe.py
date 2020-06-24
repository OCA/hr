# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeePPE(models.Model):
    """Adds PPE information and allocation."""

    _name = 'hr.employee.ppe'
    _description = 'Personal Protective Equipments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        required=True,
    )
    ppe_id = fields.Many2one(
        string='Equipment',
        required=True,
        comodel_name='hr.employee.ppe.equipment',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today()
    )
    end_date = fields.Date(
        string='End Date'
    )
    description = fields.Text(
        string='Description'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Issued By',
        help='Certification Authority'
    )
    indications = fields.Text(
        string='Indications',
        help='Situations in which the employee should use this equipment.'
    )
    expire = fields.Boolean(
        string='Expire',
        help='True if the PPE expires',
        default=True
    )
    certification = fields.Char(
        string='Certification Number',
        help='Certification Number'
    )
    status = fields.Selection(
        [('valid', 'Valid'), ('expired', 'Expired')],
        default='valid',
        readonly=True,
        help='Certification Number'
    )

    @api.onchange('ppe_id', 'employee_id', 'end_date', 'start_date')
    def verify_expiracy(self):
        if self.ppe_id and self.employee_id:
            self.name = self.ppe_id.product_id.name + _(' to ') + self.employee_id.name

        self.expire = self.ppe_id.expirable

        if not self.expire:
            self.status = 'valid'

        if self.expire and self.end_date:
            if self.end_date < fields.Date.today():
                self.status = 'expired'
            else:
                self.status = 'valid'

    @api.model
    def cron_ppe_expiry_verification(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = []
        domain.extend([('end_date', '<', date_ref)])
        ppes_to_check_expiry = self.search(domain)
        for record in ppes_to_check_expiry:
            record.status = 'expired'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if self.expire:
                if not record.end_date or not record.start_date:
                    raise ValidationError(
                        _("""You must inform start date and
                            end date for expirable PPEs.""")
                    )
                if record.end_date and record.start_date:
                    if record.end_date < record.start_date:
                        raise ValidationError(
                            _('End date cannot occur earlier than the start date.')
                        )
