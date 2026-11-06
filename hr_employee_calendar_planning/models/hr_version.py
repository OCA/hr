# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrVersion(models.Model):
    _inherit = "hr.version"

    stored_is_flexible = fields.Boolean(
        compute="_compute_stored_is_flexible", store=True
    )
    is_flexible = fields.Boolean(
        store=False, search="_search_is_flexible", compute_sudo=True
    )
    is_fully_flexible = fields.Boolean(compute="_compute_is_fully_flexible")

    def _search_is_flexible(self, operator, value):
        return [("stored_is_flexible", operator, value)]

    @api.depends("resource_calendar_id.flexible_hours")
    def _compute_stored_is_flexible(self):
        """This method is the same as _compute_is_flexible() in the hr module."""
        for version in self:
            version.stored_is_flexible = (
                version.is_fully_flexible or version.resource_calendar_id.flexible_hours
            )

    @api.depends("resource_calendar_id")
    def _compute_is_fully_flexible(self):
        """This method is the same as _compute_is_flexible() in the hr module."""
        for version in self:
            version.is_fully_flexible = version._is_fully_flexible()

    @api.depends_context(
        "flexible_hours_from_date",
        "flexible_hours_to_date",
    )
    def _compute_is_flexible(self):
        res = super()._compute_is_flexible()
        for item in self:
            item.is_flexible = (
                item.stored_is_flexible or item.resource_calendar_id.flexible_hours
            )
        return res
