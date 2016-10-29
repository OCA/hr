# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import api, models, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class RealizeInterst(models.TransientModel):
    _name = "hr.loan.realize_interest"
    _description = "Realize Loan Interest"

    date_realization = fields.Date(
        string="Date Realization",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d"),
    )

    @api.multi
    def action_realize(self):
        self.ensure_one()
        obj_schedule = self.env[
            "hr.loan.payment.schedule"]
        schedule_ids = self.env.context.get("active_ids", False)
        if not schedule_ids or len(schedule_ids) == 0:
            strWarning = _("No loan repayment schedule selected")
            raise UserError(strWarning)
        for schedule in obj_schedule.browse(schedule_ids):
            schedule.action_realize_interest(self.date_realization)
