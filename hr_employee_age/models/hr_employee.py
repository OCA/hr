# Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # The age field uses a depends (birthday) that has defined
    # groups="hr.group_hr_user", if a user without permissions in HR tries to get
    # the value of this field will have an error.
    # The correct way to avoid this inconsistency is to define groups to field age
    age = fields.Integer(compute="_compute_age", groups="hr.group_hr_user")

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthday:
                age = relativedelta(fields.Date.today(), record.birthday).years
            record.age = age
