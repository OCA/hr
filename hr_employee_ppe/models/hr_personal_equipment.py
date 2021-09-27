# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.ir_cron import _intervalTypes


class HrPersonalEquipment(models.Model):

    _name = "hr.personal.equipment"
    _inherit = ["hr.personal.equipment"]

    is_ppe = fields.Boolean()
    indications = fields.Text(
        help="Situations in which the employee should use this equipment.",
    )
    expire_ppe = fields.Boolean(help="True if the PPE expires")
    certification = fields.Char(
        string="Certification Number", help="Certification Number"
    )
    issued_by = fields.Many2one(comodel_name="res.users")

    def _accept_request_vals(self):
        res = super()._accept_request_vals()
        res["issued_by"] = self.env.user.id
        return res

    @api.onchange("product_id")
    def _compute_fields(self):
        for rec in self:
            if rec.product_id.is_ppe:
                rec.is_ppe = rec.product_id.is_ppe
                if rec.product_id.expirable_ppe:
                    rec.expire_ppe = rec.product_id.expirable_ppe
                if rec.product_id.indications:
                    rec.indications = rec.product_id.indications

    def _validate_allocation_vals(self):
        res = super()._validate_allocation_vals()
        if self.start_date:
            start_date = self.start_date
        else:
            start_date = date.today()
        if not self.expiry_date and self.product_id.expirable_ppe:
            res["expiry_date"] = start_date + _intervalTypes[
                self.product_id.ppe_interval_type
            ](self.product_id.ppe_duration)
        return res

    def validate_allocation(self):
        super().validate_allocation()
        self._check_dates()

    @api.model
    def cron_ppe_expiry_verification(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = []
        domain.extend([("expiry_date", "<", date_ref)])
        ppes_to_check_expiry = self.search(domain)
        for record in ppes_to_check_expiry:
            record.state = "expired"

    def _check_dates(self):
        for record in self:
            if record.expire_ppe:
                start_date = record.start_date if record.start_date else date.today()
                if record.expiry_date < start_date:
                    raise ValidationError(
                        _("End date cannot occur earlier than start date.")
                    )
