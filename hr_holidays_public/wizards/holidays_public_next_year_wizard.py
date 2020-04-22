# Copyright 2016 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HolidaysPublicNextYearWizard(models.TransientModel):
    _name = 'public.holidays.next.year.wizard'
    _description = 'Creates public holidays from existing ones'

    template_id = fields.Many2one(
        comodel_name='hr.holidays.public',
        string='Template',
        help='Select the public holidays to use as template.',
    )

    year = fields.Integer(
        help='Year for which you want to create the public holidays. '
        'By default, the year following the template.',
        default=fields.Date.today().year + 1
    )
    country_id = fields.Many2one(
        'res.country', string='Country', related='template_id.country_id'
    )

    pending_lines = fields.One2many(
        'hr.holidays.public.line.transient', inverse_name='wizard_id'
    )

    warning_existing = fields.Boolean(
        compute='_compute_warning_existing', store=True,
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        self.ensure_one()
        self.pending_lines = [(6, 0, [])]
        if not self.template_id:
            return
        year = self.template_id.year + 1
        vals_list = []
        for line in self.template_id.line_ids.filtered(
            lambda r: r.variable_date
        ):
            date = fields.Datetime.from_string(line.date)
            date = fields.Datetime.to_string(date.replace(year=year))
            data = (0, 0, {
                'name': line.name,
                'date': date,
                'line_id': line.id,
                'state_ids': [(6, 0, line.state_ids.ids)],
            })
            vals_list.append(data)
        self.year = year
        self.pending_lines = vals_list

    @api.onchange('year')
    def _onchange_year(self):
        self.ensure_one()
        for line in self.pending_lines:
            date = fields.Date.from_string(line.date)
            date = fields.Date.to_string(date.replace(year=self.year))
            line.date = date

    @api.depends('year', 'template_id')
    def _compute_warning_existing(self):
        for record in self:
            existing = self.env['hr.holidays.public'].search([
                ('country_id', '=', record.country_id.id),
                ('year', '=', record.year)
            ], limit=1)
            record.warning_existing = len(existing) > 0

    @api.multi
    def create_public_holidays(self):
        self.ensure_one()
        # Handling this rare case would mean quite a lot of
        # complexity because previous or next day might also be a
        # public holiday.
        if any([(
            l.date.month == 2 and l.date.day == 29
        ) for l in self.template_id.line_ids]):
            raise UserError(_(
                'You cannot use as template the public holidays '
                'of a year that includes public holidays on 29th of February'
                '(2016, 2020...), please select a template from '
                'another year.'))

        new_calendar = self.env['hr.holidays.public'].create(
            {
                'year': self.year,
                'country_id': self.country_id.id,
                'line_ids': [],
            }
        )
        for line in self.template_id.line_ids.filtered(
            lambda r: not r.variable_date
        ):
            date = fields.Date.from_string(line.date)
            date = date.replace(year=self.year)
            new_vals = {
                'year_id': new_calendar.id,
                'date': fields.Date.to_string(date),
            }
            line.copy(new_vals)

        for line in self.pending_lines:
            new_vals = {
                'year_id': new_calendar.id,
                'name': line.name,
                'date': line.date,
            }
            line.line_id.copy(new_vals)

        action = {
            'type': 'ir.actions.act_window',
            'name': 'New public holidays',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays.public',
            'res_id': new_calendar.id
        }

        return action


class PublicHolidaysLineTransient(models.TransientModel):

    _name = 'hr.holidays.public.line.transient'
    _description = 'Wizard Public Holiday Lines'
    _order = 'date'

    name = fields.Char(string='Description')
    date = fields.Date(string='Date')
    wizard_id = fields.Many2one('public.holidays.next.year.wizard')
    line_id = fields.Many2one('hr.holidays.public.line')
    state_ids = fields.Many2many('res.country.state', readonly=True)
