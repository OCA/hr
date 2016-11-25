# -*- coding: utf-8 -*-
# © 2016 MONK Software (http://www.wearemonk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def get_leave_intervals(self, resource_id=None,
                            start_datetime=None, end_datetime=None):
        """
        Extend the standard method to consider the public holidays
        """
        leaves = super(ResourceCalendar, self).get_leave_intervals(
            resource_id, start_datetime, end_datetime)

        domain = []
        if start_datetime:
            domain.append(('date', '>=', start_datetime))
        if end_datetime:
            domain.append(('date', '<=', end_datetime))
        public_holidays = self.env['hr.holidays.public.line'].search(domain)
        for ph in public_holidays:
            ph_start_datetime = fields.Datetime.from_string(ph.date)
            ph_end_datetime = (ph_start_datetime
                               + datetime.timedelta(days=1)
                               - datetime.timedelta(seconds=1))
            leaves.append((ph_start_datetime, ph_end_datetime))
        return leaves
