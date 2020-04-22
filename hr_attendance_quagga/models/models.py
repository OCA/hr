# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def attendance_scan(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the
            attendances of corresponding employee.
            Returns either an action or a warning.
        """

        employee = self.search([('barcode', '=', barcode)], limit=1)

        # prevent duplicate
        date_test = datetime.now() - timedelta(seconds=60)

        attendances = self.env['hr.attendance'].search(
            [('check_in', '>=', date_test.strftime('%Y/%m/%d, %H:%M:%S')),
             ('employee_id', '=', employee.id)])

        if len(attendances) > 0:
            return employee and {'warning': _(
                'You can scan a badge only one time per 60 seconds.')}
        else:
            # check for duplicates
            attendances = self.env['hr.attendance'].search(
                [('check_out', '>=', date_test.strftime('%Y/%m/%d, %H:%M:%S')),
                 ('employee_id', '=', employee.id)])
            if len(attendances) > 0:
                return employee and {'warning': _(
                    'You can scan a badge only one time per 60 seconds.')}
            else:
                return employee and employee.attendance_action(
                    'hr_attendance.hr_attendance_action_kiosk_mode') or \
                       {'warning': _(
                           'No employee corresponding to barcode %s') % barcode}
