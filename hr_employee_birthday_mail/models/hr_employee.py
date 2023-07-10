# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    allow_birthday_wishes = fields.Boolean(
        default=False,
        help="Check this box if you want to allow birthday wishes from our company "
        "and allow the others to be notified of your birthday.",
        groups="hr.group_hr_user",
    )
    notify_others_birthday = fields.Boolean(
        default=False,
        help="Check this box if you want to be notified about other coworkers' birthdays.",
        groups="hr.group_hr_user",
    )

    @api.model
    def _check_birthdays(self):
        today = fields.Date.today()
        employees = self.env["hr.employee"].search([])
        for employee in employees:
            if (
                employee.birthday
                and employee.birthday.day == today.day
                and employee.birthday.month == today.month
                and employee.allow_birthday_wishes
            ):
                templates_data = self.env["ir.model.data"].search(
                    [
                        ("module", "=", "hr_employee_birthday_mail"),
                        ("name", "like", "email_template_birthday_"),
                    ]
                )
                templates = self.env["mail.template"].browse(
                    [data.res_id for data in templates_data]
                )
                template = random.choice(templates)
                template.send_mail(employee.id)
                templates_coworkers_data = self.env["ir.model.data"].search(
                    [
                        ("module", "=", "hr_employee_birthday_mail"),
                        ("name", "like", "email_template_coworkers_"),
                    ]
                )
                templates_coworkers = self.env["mail.template"].browse(
                    [data.res_id for data in templates_coworkers_data]
                )
                if len(employees) > 1:
                    for coworker in employees - employee:
                        if coworker.notify_others_birthday:
                            template_coworkers = random.choice(templates_coworkers)
                            template_coworkers.with_context(
                                birthday_employee=employee.name
                            ).send_mail(coworker.id)
