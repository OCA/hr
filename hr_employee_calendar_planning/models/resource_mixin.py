# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def _list_work_time_per_day(
        self, from_datetime, to_datetime, calendar=None, domain=None
    ):
        # It is important to define the appropriate context keys so that the value is
        # as expected.
        self = self.with_context(
            flexible_hours_from_date=from_datetime.date(),
            flexible_hours_to_date=to_datetime.date(),
        )
        return super()._list_work_time_per_day(
            from_datetime, to_datetime, calendar, domain
        )
