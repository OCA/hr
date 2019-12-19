# Copyright © 2019 Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import urllib.request
from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

try:
    import vobject
except (ImportError, IOError) as err:
    _logger.debug(err)


class HrHolidaysPublic(models.Model):
    _inherit = 'hr.holidays.public'

    ics_url = fields.Char(string="ICS Url", required=False)

    @staticmethod
    def get_calendar(url):
        response = urllib.request.urlopen(url)
        return response.read().decode('utf-8')

    @api.multi
    def load_ics_calendar(self):
        holidays_line_model = self.env['hr.holidays.public.line']

        self.ensure_one()
        if self.ics_url:
            events_ics = self.get_calendar(self.ics_url)
            for cal in vobject.readComponents(events_ics):
                for component in cal.components():
                    if component.name == "VEVENT":
                        holiday_lines = holidays_line_model.search([
                            ('year_id', '=', self.id),
                            ('date', '=', datetime.strftime(component.dtstart.valueRepr(), DEFAULT_SERVER_DATE_FORMAT))
                        ])

                        if holiday_lines:
                            if component.summary.valueRepr() not in holiday_lines[0].name:
                                holiday_lines[0].name += ': ' + component.summary.valueRepr()
                        else:
                            if component.dtstart.valueRepr().year == self.year:
                                holidays_line_model.create({
                                    'name': component.summary.valueRepr(),
                                    'date': datetime.strftime(component.dtstart.valueRepr(), DEFAULT_SERVER_DATE_FORMAT),
                                    'year_id': self.id,
                                    'variable_date': False,
                                    'state_ids': False
                                })
        return True
