# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def recompute_leave_dates(self):
        """Recompute leaves if resource_calendar update after create record, although
        it is strange, it has been possible to change the work schedule"""
        for item in self:
            vals = item.read()[0]
            for key in vals:
                if isinstance(vals[key], tuple):
                    vals[key] = vals[key][0]
            virtual = self.env["hr.leave"].new(vals)
            virtual._onchange_request_parameters()
            if (
                virtual.date_from != item.date_from
                or virtual.date_to != item.date_to
            ):
                try:
                    item.write({
                        "date_from": virtual.date_from,
                        "date_to": virtual.date_to,
                    })
                    # change resource_calendar_leaves
                    resource = self.env['resource.calendar.leaves'].search([
                        ('holiday_id', '=', item.id)
                    ])
                    if resource:
                        resource.write({
                            "date_from": item.date_from,
                            "date_to": item.date_to,
                        })
                except ValidationError:
                    _logger.info("Skip: Some leaves overlap on same day")

    def _create_resource_leave(self):
        """On leave creation, trigger the recomputation of the involved
        records."""
        res = super()._create_resource_leave()
        self._check_theoretical_hours()
        return res

    def _remove_resource_leave(self):
        """On leave cancellation, trigger the recomputation of the involved
        records."""
        res = super()._remove_resource_leave()
        self._check_theoretical_hours()
        return res

    def _check_theoretical_hours(self):
        """Recomputes all the theoretical hours that corresponds to the
        interval of dates and employee of the leaves.

        :param: self: Leave recordset.
        """
        to_recompute = self.env['hr.attendance']
        for record in self.filtered(lambda x: x.date_from and x.date_to):
            from_datetime = record.date_from.replace(
                hour=0, minute=0, second=0, microsecond=0,
            )
            to_datetime = record.date_to.replace(
                hour=23, minute=59, second=59, microsecond=99999,
            )
            to_recompute |= self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', from_datetime),
                ('check_in', '<=', to_datetime),
            ])
        to_recompute._compute_theoretical_hours()
