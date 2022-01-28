# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrLeave(models.Model):

    _inherit = "hr.leave"

    request_time_hour_from = fields.Float("Float hour from")

    request_hour_from = fields.Char(compute="_compute_hour_from", store=True)

    request_time_hour_to = fields.Float("Float hour to")

    request_hour_to = fields.Char(compute="_compute_hour_to", store=True)

    @api.depends("request_time_hour_from")
    def _compute_hour_from(self):
        for leave in self:
            leave.request_hour_from = "%.2f" % self.request_time_hour_from

    @api.depends("request_time_hour_to")
    def _compute_hour_to(self):
        for leave in self:
            leave.request_hour_to = "%.2f" % self.request_time_hour_to

    @api.onchange(
        "request_date_from_period",
        "request_time_hour_from",
        "request_time_hour_to",
        "request_date_from",
        "request_date_to",
        "employee_id",
    )
    def _onchange_request_parameters(self):
        return super(HrLeave, self)._onchange_request_parameters()
