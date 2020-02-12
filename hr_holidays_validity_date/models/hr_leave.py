# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    restrict_dates = fields.Boolean(
        string="Restrict",
        help="Check this if you want to forbid requesting "
             "leaves outside this range, otherwise it will just "
             "display a warning to the user."
    )


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    warning_validity = fields.Char(
        compute='_compute_warning_range',
        oldname='warning',
    )
    restrict_dates = fields.Boolean(string='Restrict dates',
                                    related='holiday_status_id.restrict_dates')

    @api.depends('holiday_status_id', 'date_from', 'date_to')
    def _compute_warning_range(self):
        for rec in self:
            if rec.holiday_status_id.validity_start and (
                    rec.holiday_status_id.validity_stop
            ):
                rec.warning_validity = False
                vstart = rec.holiday_status_id.validity_start
                vstop = rec.holiday_status_id.validity_stop
                dfrom = rec.date_from
                dto = rec.date_to

                if dfrom and dto and (
                        dfrom.date() < vstart or dto.date() > vstop
                ):
                        rec.warning_validity = _(
                            'Warning: You can take %s only between %s and %s'
                        ) % (rec.holiday_status_id.display_name,
                             rec.holiday_status_id.validity_start,
                             rec.holiday_status_id.validity_stop)

    @api.multi
    @api.constrains('holiday_status_id', 'date_to', 'date_from')
    def _check_leave_type_validity(self):
        super(
            HolidaysRequest,
            self.filtered('restrict_dates')
        )._check_leave_type_validity()
