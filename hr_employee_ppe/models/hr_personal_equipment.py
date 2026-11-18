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
        string="Certification Number",
        help="Certificate of approval the equipment was handed over under. "
        "Copied from the product when the request is accepted and kept "
        "unchanged afterwards: an inspection asks which certificate was valid "
        "on the delivery date, so renewing the product's certificate must not "
        "rewrite deliveries already made.",
    )
    certification_expiry_date = fields.Date(
        help="Expiry date of the certificate of approval the equipment was "
        "handed over under. Frozen at delivery, like the certificate number.",
    )
    issued_by = fields.Many2one(comodel_name="res.users")

    def _accept_request_vals(self):
        res = super()._accept_request_vals()
        res["issued_by"] = self.env.user.id
        res.update(self._ppe_certification_vals())
        return res

    def _ppe_certification_vals(self):
        """Freeze the product's certificate of approval on the allocation.

        Read from the product at acceptance instead of a related field: the
        allocation is the record of a delivery to a named worker on a given
        date, and a related field would rewrite every past delivery as soon as
        the certificate is renewed.
        """
        self.ensure_one()
        if not self.product_id.is_ppe:
            return {}
        return {
            "certification": self.certification or self.product_id.ppe_certification,
            "certification_expiry_date": (
                self.certification_expiry_date
                or self.product_id.ppe_certification_expiry_date
            ),
        }

    def _check_certification_valid(self):
        """Refuse to hand over equipment whose certificate has expired."""
        today = fields.Date.context_today(self)
        for record in self:
            expiry = record.product_id.ppe_certification_expiry_date
            if record.product_id.is_ppe and expiry and expiry < today:
                raise ValidationError(
                    _(
                        "The certificate of approval of %(product)s expired on "
                        "%(expiry)s. Expired equipment cannot be handed over; "
                        "renew the certificate on the product first."
                    )
                    % {"product": record.product_id.display_name, "expiry": expiry}
                )

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
        res = super().validate_allocation()
        self._check_dates()
        return res

    def _accept_request(self):
        self._check_certification_valid()
        return super()._accept_request()

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
