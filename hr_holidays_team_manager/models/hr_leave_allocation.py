# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models
from odoo.exceptions import ValidationError


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def action_validate(self):
        if self.env.user.has_group(
            "hr_holidays.group_hr_holidays_user"
        ) and not self.env.user.has_group(
            "hr_holidays_team_manager.group_hr_holidays_officer"
        ):
            raise ValidationError(_("Team managers can't approve time off allocations"))
        return super().action_validate()
