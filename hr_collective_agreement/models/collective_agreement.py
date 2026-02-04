# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CollectiveAgreement(models.Model):
    _name = "collective.agreement"
    _description = "Collective Agreement"
    _check_company_auto = True

    code = fields.Char(required=True)
    name = fields.Text(required=True)
    scope_id = fields.Many2one(
        comodel_name="collective.agreement.scope",
        string="Scope",
        required=True,
    )
    publication_date = fields.Date(required=True)
    end_date = fields.Date()
    official_publication_id = fields.Many2one(
        comodel_name="collective.agreement.official.publication",
        string="Official Publication",
        required=True,
    )
    observations = fields.Text()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("finished", "Finished"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    active = fields.Boolean(default=True)
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="collective_agreement_partner_rel",
        column1="agreement_id",
        column2="partner_id",
        string="Partners",
        check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code must be unique"),
        ("name_uniq", "unique(name)", "The name must be unique"),
    ]

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for agreement, vals in zip(self, vals_list, strict=False):
            if "code" not in default:
                vals["code"] = _("%s (copy)", agreement.code)
            if "name" not in default:
                vals["name"] = _("%s (copy)", agreement.name)
            vals["state"] = "draft"
        return vals_list

    @api.constrains("end_date", "publication_date")
    def _check_end_date(self):
        for record in self:
            if record.end_date and record.end_date < record.publication_date:
                raise ValidationError(
                    _("The end date cannot be earlier than the publication date.")
                )

    def action_draft(self):
        self.write({"state": "draft"})

    def action_activate_agreement(self):
        today = fields.Date.today()
        expired = self.filtered(lambda r: r.end_date and r.end_date < today)
        if expired:
            raise ValidationError(
                _(
                    'The collective agreements "%s" cannot be activated '
                    "because their end date has already passed.",
                    ", ".join(expired.mapped("code")),
                )
            )
        self.write({"state": "active"})

    def action_finish(self):
        invalid = self.filtered(lambda r: r.state != "active")
        if invalid:
            raise ValidationError(
                _(
                    'The collective agreements "%s" cannot be finished '
                    "because they are not in active state.",
                    ", ".join(invalid.mapped("code")),
                )
            )
        self.write({"state": "finished"})

    def action_cancel(self):
        invalid = self.filtered(lambda r: r.state in ("finished", "cancelled"))
        if invalid:
            raise ValidationError(
                _(
                    'The collective agreements "%s" cannot be cancelled '
                    "because they are already finished or cancelled.",
                    ", ".join(invalid.mapped("code")),
                )
            )
        self.write({"state": "cancelled"})

    def action_update_states(self):
        today = fields.Date.today()
        to_finish = self.search(
            [
                ("state", "in", ("draft", "active")),
                ("end_date", "!=", False),
                ("end_date", "<", today),
            ]
        )
        to_finish.write({"state": "finished"})
        to_activate = self.search(
            [
                ("state", "=", "draft"),
                "|",
                ("end_date", "=", False),
                ("end_date", ">=", today),
            ]
        )
        to_activate.write({"state": "active"})
