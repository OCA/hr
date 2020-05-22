# Copyright 2019 Creu Blanca
# Copyright 2020 Landoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class TestHrAttendanceTracking(TransactionCase):

    def setUp(self):
        super(TestHrAttendanceTracking, self).setUp()
        self.hr_attendance = self.env['hr.attendance']

    def test_attendance_edit(self):
        # We can't check kiosk and check-in/check-out form
        # So we will check attendance creation from form view
        #####################################################
        # Use case 1:
        # Create an attendance with correct (now) check-in and leave it open
        # Expected: manually_changed = False
        self.employee_01 = self.env['hr.employee'].create({'name': 'Employee01'})
        dti = datetime.now()
        att = self.hr_attendance.create({'employee_id': self.employee_01.id,
                                         'check_in': dti.strftime(DF),
                                         })
        self.assertEqual(att.time_changed_manually, False, "Use case 1: Wrong value,"
                                                           " not changes.")
        # Use case 2:
        # Create an attendance with incorrect (now - 10 minutes) check-in and
        # leave it open. Maximum tolerance is one minute from now.
        # Expected: manually_changed = True
        self.employee_02 = self.env['hr.employee'].create({'name': 'Employee02'})
        dti = datetime.now() - relativedelta(minutes=10)
        att = self.hr_attendance.create({'employee_id': self.employee_02.id,
                                         'check_in': dti.strftime(DF),
                                         })
        self.assertEqual(att.time_changed_manually, True, "Use case 2: Wrong value, "
                                                          "tolerance exceeded")
        # Use case 3:
        # Create an attendance with incorrect (now + 10 minutes) check-in
        # and leave it open.Maximum tolerance is one minute from now.
        # Expected: manually_changed = True
        self.employee_03 = self.env['hr.employee'].create({'name': 'Employee03'})
        dti = datetime.now() + relativedelta(minutes=10)
        att = self.hr_attendance.create({'employee_id': self.employee_03.id,
                                         'check_in': dti.strftime(DF),
                                         })
        self.assertEqual(att.time_changed_manually, True, "Use case 3: Wrong value, "
                                                          "tolerance exceeded.")
        # Use case 4:
        # Create an attendance with correct (now - 15 sec) check-in and correct
        # (now + 15 sec) check-out.
        # Expected: manually_changed = False
        self.employee_04 = self.env['hr.employee'].create({'name': 'Employee04'})
        dti = datetime.now() - relativedelta(seconds=15)
        dto = datetime.now() + relativedelta(seconds=15)
        att = self.hr_attendance.create({'employee_id': self.employee_04.id,
                                         'check_in': dti.strftime(DF),
                                         'check_out': dto.strftime(DF),
                                         })
        self.assertEqual(att.time_changed_manually, False, "Use case 4: Wrong value, "
                                                           "tolerance not exceeded.")
        # Use case 5:
        # Change previous attendance check-out to now + 1 hour
        # Expected: manually_changed = True
        dto = datetime.now() + relativedelta(hours=1)
        att.write({'check_out': dto.strftime(DF)})
        self.assertEqual(att.time_changed_manually, True, "Use case 5: Wrong value, "
                                                          "data changed.")
        # Use case 6:
        # Create an attendance with correct (now - 15 sec) check-in and incorrect
        # (now + 15 min) check-out
        # Expected: manually_changed = True
        self.employee_05 = self.env['hr.employee'].create({'name': 'Employee05'})
        dti = datetime.now() - relativedelta(seconds=15)
        dto = datetime.now() + relativedelta(minutes=15)
        att = self.hr_attendance.create({'employee_id': self.employee_05.id,
                                         'check_in': dti.strftime(DF),
                                         'check_out': dto.strftime(DF),
                                         })
        self.assertEqual(att.time_changed_manually, True, "Use case 6 : Wrong value, "
                                                          "tolerance exceeded.")
