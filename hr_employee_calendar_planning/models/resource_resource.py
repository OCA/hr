# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResourceResource(models.Model):
    _inherit = "resource.resource"

    def _get_calendar_at(self, date_target, tz=False):
        # It is important to define the context keys so that the value is as expected
        # (for example, the 'flexible_hours' field); this method is used within
        # _attendance_intervals_batch() in resource, which in turn is used in many
        # processes.
        self = self.with_context(
            flexible_hours_from_date=date_target.date(),
            flexible_hours_to_date=date_target.date(),
        )
        return super()._get_calendar_at(date_target=date_target, tz=tz)
