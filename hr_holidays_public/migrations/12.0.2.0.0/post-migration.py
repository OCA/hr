# Copyright 2019 Druidoo - Iván Todorovich <ivan.todorovich@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        holidays_without_meeting = env['hr.holidays.public.line'].search([
            ('meeting_id', '=', False)])
        for holiday in holidays_without_meeting:
            _logger.debug('Creating meeting for holiday: %s' % holiday.name)
            holiday.meeting_id = env['calendar.event'].create(
                holiday._prepare_holidays_meeting_values())
