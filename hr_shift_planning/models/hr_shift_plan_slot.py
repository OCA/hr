# Copyright 2025 Open SOurce Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrShiftPlanSlot(models.Model):
    _name = "hr.shift.plan.slot"
    _description = "Shift Plan Slot"

    template_id = fields.Many2one("hr.shift.plan.template")
    day = fields.Integer()
    time_period_id = fields.Many2one("hr.shift.timeperiod")
    position_id = fields.Many2one("hr.shift.position")
