# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    employee_names_order = fields.Selection(
        string="Employee names order",
        selection="_employee_names_order_selection",
        help="Order to compose employee fullname",
        required=True,
    )
    employee_names_order_changed = fields.Boolean(
        compute="_compute_names_order_changed",
    )

    def _employee_names_order_selection(self):
        return [
            ('last_first', 'Lastname Firstname'),
            ('last_first_comma', 'Lastname, Firstname'),
            ('first_last', 'Firstname Lastname'),
        ]

    @api.multi
    def _employee_names_order_default(self):
        return self.env['hr.employee']._names_order_default()

    @api.model
    def get_default_employee_names_order(self, fields):
        return {
            'employee_names_order': self.env['ir.config_parameter'].get_param(
                'employee_names_order', self._employee_names_order_default(),
            ),
        }

    @api.multi
    @api.depends('employee_names_order')
    def _compute_names_order_changed(self):
        current = self.env['ir.config_parameter'].get_param(
            'employee_names_order', self._employee_names_order_default(),
        )
        for record in self:
            record.employee_names_order_changed = bool(
                record.employee_names_order != current
            )

    @api.multi
    @api.onchange('employee_names_order')
    def _onchange_employee_names_order(self):
        self.employee_names_order_changed = self._compute_names_order_changed()

    @api.multi
    def set_employee_names_order(self):
        self.env['ir.config_parameter'].set_param(
            'employee_names_order', self.employee_names_order)

    @api.multi
    def _employees_for_recalculating(self):
        return self.env['hr.employee'].search([
            ('firstname', '!=', False), ('lastname', '!=', False),
        ])

    @api.multi
    def action_recalculate_employees_name(self):
        employees = self._employees_for_recalculating()
        _logger.info("Recalculating names for %d employees.", len(employees))
        employees.get_name()
        _logger.info("%d employees updated.", len(employees))
        return True
