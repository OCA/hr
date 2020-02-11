# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('user_id')
    def _compute_display_personal_data(self):
        for employee in self:
            employee.employee_display_personal_data = False
            if self.user_has_groups('hr.group_hr_user'):
                employee.employee_display_personal_data = True
            elif employee.user_id == self.env.user:
                employee.employee_display_personal_data = True

    employee_display_personal_data = fields.Boolean(
        compute='_compute_display_personal_data'
    )

    # Citizenship & Other Information
    country_id = fields.Many2one(groups=False)
    identification_id = fields.Char(groups=False)
    passport_id = fields.Char(groups=False)
    bank_account_id = fields.Many2one(groups=False)

    # Contact Information
    address_home_id = fields.Many2one(groups=False)
    emergency_contact = fields.Char(groups=False)
    emergency_phone = fields.Char(groups=False)
    km_home_work = fields.Integer(groups=False)

    # Status
    gender = fields.Selection(groups=False)
    marital = fields.Selection(groups=False)
    children = fields.Integer(groups=False)

    # Birth
    birthday = fields.Date(groups=False)
    place_of_birth = fields.Char(groups=False)
    country_of_birth = fields.Many2one(groups=False)

    # Work Permit
    visa_no = fields.Char(groups=False)
    permit_no = fields.Char(groups=False)
    visa_expire = fields.Date(groups=False)

    # Education
    certificate = fields.Selection(groups=False)
    study_field = fields.Char(groups=False)
    study_school = fields.Char(groups=False)

    google_drive_link = fields.Char(groups=False)
    additional_note = fields.Text(groups=False)
