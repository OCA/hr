#  Copyright 2025- Le Filament (https://le-filament.com)
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    def action_validate_with_error(self):
        res = self.action_validate()
        if not res:
            raise ValidationError(
                _(
                    "Some entries are in conflict and cannot be validated, "
                    "please solve conflicts first."
                )
            )
        return res

    def validate_work_entries(self, employee_id, date_start, date_stop):
        date_start = datetime.combine(fields.Date().from_string(date_start), time.min)
        date_stop = date_start = datetime.combine(
            fields.Date().from_string(date_stop), time.max
        )
        work_entries = self.search(
            [
                ("employee_id", "=", int(employee_id)),
                ("date_start", ">=", date_start),
                ("date_stop", "<=", date_stop),
            ]
        )
        return work_entries.action_validate()
