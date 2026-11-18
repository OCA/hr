# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _name = "product.template"
    _inherit = ["product.template"]

    is_ppe = fields.Boolean(default=False)
    indications = fields.Text(
        help="Situations in which the employee should use this equipment. Only for ppe",
    )
    expirable_ppe = fields.Boolean(
        help="Select this option if the PPE has expiry date.", default=False
    )
    ppe_duration = fields.Integer(string="PPE duration")
    ppe_interval_type = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Interval Unit",
    )
    ppe_certification = fields.Char(
        string="PPE Certification Number",
        help="Number of the certificate of approval issued by the competent "
        "authority for this equipment. It belongs to the equipment, not to a "
        "particular delivery.",
    )
    ppe_certification_expiry_date = fields.Date(
        string="PPE Certification Expiry Date",
        help="Date the certificate of approval itself expires. This is not the "
        "service life of the equipment for a worker (see PPE Duration): a "
        "certificate expires on the same date for every unit of the product, "
        "whoever is wearing it.",
    )
    ppe_certification_expired = fields.Boolean(
        compute="_compute_ppe_certification_expired",
        help="Technical field: the certificate of approval is past its expiry "
        "date, so the equipment can no longer be handed to a worker.",
    )

    @api.depends("ppe_certification_expiry_date")
    def _compute_ppe_certification_expired(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.ppe_certification_expired = bool(
                record.ppe_certification_expiry_date
                and record.ppe_certification_expiry_date < today
            )
