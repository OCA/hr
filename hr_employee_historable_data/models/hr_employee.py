# Copyright 2021 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    work_permit_ids = fields.One2many(
        string="Work permit",
        comodel_name="hr.employee.workpermit",
        inverse_name="employee_id",
    )
    marital_status_ids = fields.One2many(
        string="Marital status",
        comodel_name="hr.employee.marital",
        inverse_name="employee_id",
    )
    marital = fields.Selection(compute="_compute_marital_status")
    visa_no = fields.Char(compute="_compute_visa_no")

    @api.depends("marital_status_ids.date_start", "marital_status_ids.date_end", "marital_status_ids.marital")
    def _compute_marital_status(self):
        for rec in self:
            states = rec.mapped("marital_status_ids").filtered(
                lambda c: c.date_start <= fields.Date.today()
                and c.date_end >= fields.Date.today()
            )
            if states:
                rec.marital = states[0].marital
            else:
                rec.marital = False
    # TODO finis work permit handling
    @api.depends("work_permit_ids.date_start", "work_permit_ids.date_end", "work_permit_ids.visa", "work_permit_ids.permit_no")
    def _compute_visa_no(self):
        for rec in self:
            states = rec.mapped("work_permit_ids").filtered(
                lambda c: c.date_start <= fields.Date.today()
                and c.date_end >= fields.Date.today()
            )
            if states:
                rec.update({
                    "visa_no": states[0].visa,
                    "visa_expire": states[0].date_end,
                })
            else:
                rec.update({
                    "visa_no": False,
                    "visa_expire": False,
                })

