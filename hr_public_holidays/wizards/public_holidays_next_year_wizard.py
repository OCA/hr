# -*- coding: utf-8 -*-
# Copyright 2016 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class PublicHolidaysNextYearWizard(models.TransientModel):
    _name = 'public.holidays.next.year.wizard'
    _description = 'Creates public holidays for the year following the last'

    @api.multi
    def create_next_year_public_holidays(self):

        ph_env = self.env['hr.holidays.public']
        pholidays = ph_env.search([])

        NO_COUNTRY = 'NO_COUNTRY'
        last_ph_dict = {}
        for ph in pholidays:

            curr_country = ph.country_id and ph.country_id.id or NO_COUNTRY
            last_ph_country = last_ph_dict.get(curr_country, False)

            if last_ph_country:
                if last_ph_country.year < ph.year:
                    last_ph_dict[curr_country] = ph
            else:
                last_ph_dict[curr_country] = ph

        new_ph_ids = []
        for last_ph in last_ph_dict.itervalues():

            new_ph_vals = {
                'year': last_ph.year + 1,
            }
            new_ph = last_ph.copy(new_ph_vals)

            new_ph_ids.append(new_ph.id)

            for last_ph_line in last_ph.line_ids:

                ph_line_date = fields.Date.from_string(last_ph_line.date)
                new_date = ph_line_date.replace(ph_line_date.year + 1)

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
