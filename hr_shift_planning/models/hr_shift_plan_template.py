# Copyright 2025 Open SOurce Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class HrShiftPlanTemplate(models.Model):
    _name = "hr.shift.plan.template"
    _description = "Shift Plan Template"

    name = fields.Char(required=True, translate=True)
    time_periods_ids = fields.Many2many("hr.shift.timeperiod")
    positions_ids = fields.Many2many("hr.shift.position")
    cycle_days = fields.Integer()
    plan_slots_ids = fields.One2many("hr.shift.plan.slot", "template_id")

    def populate_missing_slots(self):
        for template in self:
            existing = self.search([("template_id", "=", template.id)])
            needed = [
                (day, time_period)
                for day in range(1, template.cycle_days + 1)
                for time_period in template.time_periods_ids
                if not existing.filtered(
                    lambda x, day=day, time_period=time_period: x.day == day
                    and x.time_period_id == time_period
                )
            ]
            to_create_values = [
                {
                    "template_id": template.id,
                    "day": day,
                    "time_period_id": time_period.id,
                }
                for day, time_period in needed
            ]
            template.plan_slots_ids.create(to_create_values)

    @api.create_multi
    def create(self, values):
        res = super().create(values)
        res.populate_missing_slots()
        return res

    def write(self, values):
        res = super().write(values)
        res.populate_missing_slots()
        return res
