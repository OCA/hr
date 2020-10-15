# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def _get_work_hours(self, start, stop, meta):
        """
        This method now returns the hours between the two ends of the
        interval. Extend this method if you want to alter the logic.
        :param interval:
        :return: float representing the time worked.
        """
        return (stop - start).total_seconds() / 3600
