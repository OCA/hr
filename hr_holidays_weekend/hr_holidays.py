# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Andy Kanner <andy.kenner@initos.com>
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone, utc
import datetime
import math


class hr_holidays(orm.Model):

    _inherit = 'hr.holidays'

    def get_public_holidays(self, cr, uid, employee_id):
        holidays = []

        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)

        hr_holiday_public_obj = self.pool.get('hr.holidays.public')
        if employee.address_id.country_id == None:
            country_filter = [('country_id', '=', False)]
        else:
            country_filter = ['|', ('country_id', '=',
                                          employee.address_id.country_id.id),
                                         ('country_id', '=', False)]
        hr_holiday_public = hr_holiday_public_obj.search(cr, uid,
                                        country_filter)

        if employee.address_id.state_id == None:
            states_filter = [('holidays_id', 'in',
                                           hr_holiday_public),
                                          ('state_ids', '=', False)]
        else:
            states_filter = [('holidays_id', 'in',
                                            hr_holiday_public),
                                          '|', ('state_ids.id', '=',
                                          employee.address_id.state_id.id),
                                          ('state_ids', '=', False)]

        hr_holiday_public_line_obj = self.pool.get('hr.holidays.public.line')
        holidays_line_ids = hr_holiday_public_line_obj.search(cr, uid,
                                        states_filter)
        for holiday_line_id in holidays_line_ids:
            line = hr_holiday_public_line_obj.browse(cr, uid, holiday_line_id)
            holidays.append(line.date)
        return holidays

    def onchange_date_from(self, cr, uid, ids, date_to, date_from,
                            employee_id):
        """
        If there are no date set for date_to, automatically
        set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise orm.except_orm(_('Warning!'), _("""The start date must be
                anterior to the end date."""))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta =\
                datetime.datetime.strptime(date_from,
                                           DEFAULT_SERVER_DATETIME_FORMAT) +\
                                           datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # new timezone-shift
        user_obj = self.pool.get("res.users").browse(cr, uid, uid)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr, uid, date_from, date_to,
                                                 user_obj.tz,
                                                 user_obj.tz_offset,
                                                 employee_id)
            result['value']['number_of_days_temp'] =\
                round(math.floor(diff_day))
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from, employee_id):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise orm.except_orm(_('Warning!'), _("""The start date must
                                                    be anterior to
                                                    the end date."""))

        result = {'value': {}}

        # new timezone-shift
        user_obj = self.pool.get("res.users").browse(cr, uid, uid)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr, uid, date_from,
                                                 date_to, user_obj.tz,
                                                 user_obj.tz_offset,
                                                 employee_id)
            result['value']['number_of_days_temp'] =\
                round(math.floor(diff_day))
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def _get_number_of_days(self, cr, uid, date_from, date_to,
                             tz, tz_offset, employee_id):

        """Returns a float equals to the timedelta between
        two dates given as string.NEW: without weekend days"""

        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)

        # parse and reduce to date viewing
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        from_full = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_full = datetime.datetime.strptime(date_to, DATETIME_FORMAT)

        # user-timezone is configured
        if tz:

            local_tz = timezone(tz)

            # utc info
            utc_date_from = from_full.replace(tzinfo=utc)
            utc_date_to = to_full.replace(tzinfo=utc)

            # Shift based on timezone and daylight savings
            from_tz = local_tz.normalize(utc_date_from.astimezone(local_tz))
            to_tz = local_tz.normalize(utc_date_to.astimezone(local_tz))

            # extract date
            from_dt = from_tz.date()
            to_dt = to_tz.date()

        else:

            # extract date if timezone unset
            from_dt = from_full.date()
            to_dt = to_full.date()

        delta_single_day = datetime.timedelta(days=1)

        # iteration data
        current_dt = from_dt
        res_diff_days = 0

        # integers for Saturday and Sunday
        # weekend_set = set([5, 6])

        if(employee.work_days == '5'):
            lst_weekend_int_values = [5, 6]
        else:
            lst_weekend_int_values = [6]

        lst_holidays = self.get_public_holidays(cr, uid, employee_id)
        while current_dt <= to_dt:
            # if it is not a weekend day
            if current_dt.weekday() not in lst_weekend_int_values and\
                    current_dt.strftime('%Y-%m-%d') not in lst_holidays:
                res_diff_days += 1
            # current_dt not in lst_holidays:
            current_dt += delta_single_day

        # return result
        return res_diff_days
