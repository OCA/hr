from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    hr_employee_ids = fields.One2many(
        "hr.employee",
        "partner_id",
        "Employee",
        auto_join=True,
        help="Partner associated employee, technical for one2one",
    )
    hr_employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        help="Partner associated employee",
        compute="_compute_hr_employee_id",
        inverse="_inverse_hr_employee_id",
    )

    is_employee = fields.Boolean(
        compute="_compute_is_employee",
        help="Check if the partner is an employee",
    )

    @api.depends("hr_employee_id")
    def _compute_is_employee(self):
        for rec in self:
            rec.is_employee = True if rec.hr_employee_ids else False

    @api.depends("hr_employee_ids")
    def _compute_hr_employee_id(self):
        for rec in self:
            if rec.hr_employee_ids:
                rec.hr_employee_id = rec.hr_employee_ids[0]
            else:
                rec.hr_employee_id = False

    def _inverse_hr_employee_id(self):
        for rec in self:
            if rec.hr_employee_id:
                rec.hr_employee_ids = [(6, 0, rec.hr_employee_id.id)]
            else:
                rec.hr_employee_ids = [(5,)]
