# Copyright 2016 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HolidaysPublicNextYearWizard(models.TransientModel):
    _name = 'public.holidays.next.year.wizard'
    _description = 'Creates public holidays from existing ones'

    template_ids = fields.Many2many(
        comodel_name='hr.holidays.public',
        string='Templates',
        help='Select the public holidays to use as template. '
        'If not set, latest public holidays of each country will be used. '
        'Only the last templates of each country for each year will '
        'be taken into account (If you select templates from 2012 and 2015, '
        'only the templates from 2015 will be taken into account.',)
    year = fields.Integer(
        help='Year for which you want to create the public holidays. '
        'By default, the year following the template.',
    )

    @api.multi
    def create_public_holidays(self):

        self.ensure_one()

        last_ph_dict = {}

        ph_env = self.env['hr.holidays.public']
        pholidays = self.template_ids or ph_env.search([])

        if not pholidays:
            raise UserError(_(
                'No Public Holidays found as template. '
                'Please create the first Public Holidays manually.'))

        for ph in pholidays:

            last_ph_country = last_ph_dict.get(ph.country_id, False)

            if last_ph_country:
                if last_ph_country.year < ph.year:
                    last_ph_dict[ph.country_id] = ph
            else:
                last_ph_dict[ph.country_id] = ph

        new_ph_ids = []
        for last_ph in last_ph_dict.values():

            new_year = self.year or last_ph.year + 1

            new_ph_vals = {
                'year': new_year,
            }

            new_ph = last_ph.copy(new_ph_vals)

            new_ph_ids.append(new_ph.id)

            for last_ph_line in last_ph.line_ids:
                feb_29 = (
                    last_ph_line.date.month == 2 and
                    last_ph_line.date.day == 29)

                if feb_29:
                    # Handling this rare case would mean quite a lot of
                    # complexity because previous or next day might also be a
                    # public holiday.
                    raise UserError(_(
                        'You cannot use as template the public holidays '
                        'of a year that '
                        'includes public holidays on 29th of February '
                        '(2016, 2020...), please select a template from '
                        'another year.'))

                new_date = last_ph_line.date.replace(year=new_year)

                new_ph_line_vals = {
                    'date': new_date,
                    'year_id': new_ph.id,
                }
                last_ph_line.copy(new_ph_line_vals)

        domain = [['id', 'in', new_ph_ids]]

        action = {
            'type': 'ir.actions.act_window',
            'name': 'New public holidays',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays.public',
            'domain': domain
        }

        return action
