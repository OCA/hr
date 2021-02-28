# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeePPE(models.Model):
    """Adds PPE information and allocation."""

    _name = "hr.employee.ppe"
    _description = "Personal Protective Equipments"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name",)
    ppe_id = fields.Many2one(
        string="Equipment", required=True, comodel_name="hr.employee.ppe.equipment",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=True
    )
    start_date = fields.Date(string="Start Date", default=fields.Date.today())
    end_date = fields.Date(string="End Date")
    description = fields.Text(string="Description")
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Issued By", help="Certification Authority"
    )
    indications = fields.Text(
        string="Indications",
        help="Situations in which the employee should use this equipment.",
    )
    expire = fields.Boolean(
        string="Expire", help="True if the PPE expires", default=True,
    )
    certification = fields.Char(
        string="Certification Number", help="Certification Number"
    )
    status = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")],
        compute="_compute_status",
        readonly=True,
        help="PPE Status",
    )

    @api.depends("ppe_id", "employee_id")
    def _compute_name(self):
        for rec in self:
            if rec.ppe_id.product_id.name and rec.employee_id.name:
                rec.name = rec.ppe_id.product_id.name + _(" to ") + rec.employee_id.name
                rec.expire = rec.ppe_id.expirable

    @api.depends("end_date", "start_date")
    def _compute_status(self):
        for rec in self:
            if not rec.expire:
                rec.status = "valid"
            if rec.expire and rec.end_date:
                if rec.end_date < fields.Date.today():
                    rec.status = "expired"
                else:
                    rec.status = "valid"

    @api.model
    def cron_ppe_expiry_verification(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = []
        domain.extend([("end_date", "<", date_ref)])
        ppes_to_check_expiry = self.search(domain)
        for record in ppes_to_check_expiry:
            record.status = "expired"

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if self.expire:
                if not record.end_date or not record.start_date:
                    raise ValidationError(
                        _(
                            """You must inform start date and
                            end date for expirable PPEs."""
                        )
                    )
                if record.end_date and record.start_date:
                    if record.end_date < record.start_date:
                        raise ValidationError(
                            _("End date cannot occur earlier than the start date.")
                        )
