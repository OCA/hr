# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardGenerateCalendarPlanning(models.TransientModel):
    _name = "wizard.generate.calendar.planning"
    _description = (
        "Generation wizard to allow generate calendar planning for N employees"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get("active_id")
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")

        if not active_ids or active_model != "hr.employee":
            return res
        res["employee_id"] = active_id
        res["employee_ids"] = [(6, 0, active_ids)]
        return res

    calendar_ids = fields.Many2many(
        comodel_name="hr.employee.calendar",
        string="Calendar planning",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
    )
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employees")

    def create_calendar_planning(self):
        for employee in self.employee_ids - self.employee_id:
            for calendar in self.calendar_ids:
                calendar.copy(
                    {
                        "employee_id": employee.id,
                    }
                )
