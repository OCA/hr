# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import Form, TransactionCase
from odoo.exceptions import UserError


class TestAttendanceSheet(TransactionCase):
    def setUp(self):
        super(TestAttendanceSheet, self).setUp()
        self.AttendanceSheet = self.env["hr.attendance.sheet"]
        employee_group = self.env.ref("hr_attendance.group_hr_attendance_user")
        manager_group = self.env.ref("hr_attendance.group_hr_attendance_manager")
        self.test_user_manager = self.env["res.users"].create(
            {
                "name": "Test User Manager",
                "login": "test",
                "email": "test@test.com",
                "groups_id": [(4, manager_group.id)],
            }
        )
        self.test_user_employee = self.env["res.users"].create(
            {
                "name": "Test User Employee",
                "login": "test2",
                "email": "test2@test.com",
                "groups_id": [(4, employee_group.id)],
            }
        )
        self.test_manager = self.env["hr.employee"].create(
            {
                "name": "TestManager",
                "user_id": self.test_user_manager.id,
                "manual_attendance": True,
                "use_attendance_sheets": True,
                "hours_to_work": 80,
            }
        )
        self.test_employee = self.env["hr.employee"].create(
            {
                "name": "TestEmployee",
                "user_id": self.test_user_employee.id,
                "parent_id": self.test_manager.id,
                "manual_attendance": True,
                "use_attendance_sheets": True,
                "hours_to_work": 80,
            }
        )
        self.test_attendance1 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": fields.Date.today().strftime("%Y-%m-%d 08:00"),
                "check_out": fields.Date.today().strftime("%Y-%m-%d 12:00"),
            }
        )
        self.test_attendance2 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": fields.Date.today().strftime("%Y-%m-%d 13:00"),
                "check_out": fields.Date.today().strftime("%Y-%m-%d 17:00"),
            }
        )

    def test_attendance_sheet(self):
        company = self.env.user.company_id
        company.write(
            {
                "use_attendance_sheets": True,
                "date_start": fields.Date.today(),
                "attendance_sheet_range": "WEEKLY",
                "auto_lunch": True,
                "auto_lunch_duration": 0.5,
                "auto_lunch_hours": 0.5,
            }
        )

        # TEST01: Test create sheet method
        view_id = "hr_attendance_sheet.hr_attendance_sheet_view_form"
        with Form(self.AttendanceSheet, view=view_id) as f:
            f.employee_id = self.test_employee
            f.date_start = fields.Date.today()
            f.date_end = fields.Date.today() + timedelta(days=14)
        sheet = f.save()
        self.assertEqual(len(sheet.attendance_ids), 2)

        # TEST02: Test new attendance linked to sheet
        self.test_attendance3 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": fields.Date.today().strftime("%Y-%m-%d 18:00"),
                "check_out": fields.Date.today().strftime("%Y-%m-%d 19:00"),
            }
        )
        self.assertEqual(len(sheet.attendance_ids), 3)

        # TEST03: Test sheet confirm with incorrect attendances
        self.test_attendance_inprogress = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": fields.Date.today().strftime("%Y-%m-%d 22:00"),
            }
        )
        with self.assertRaises(UserError):
            sheet.action_attendance_sheet_confirm()
        self.test_attendance_inprogress.unlink()

        # TEST04: Test sheet confirm
        sheet.action_attendance_sheet_confirm()
        self.assertEqual(sheet.state, "confirm")

        # TEST05: Test sheet draft error when in confirm
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_manager).action_attendance_sheet_draft()

        # TEST06: Test sheet lock error when not approved
        with self.assertRaises(UserError):
            sheet.action_attendance_sheet_lock()

        # TEST07: Test sheet done (Not Reviewer)
        with self.assertRaises(UserError):
            sheet.action_attendance_sheet_done()

        # TEST08: Test sheet done with open attendance error
        clockin_date = fields.Date.today() + timedelta(days=4)
        self.test_attendance_open = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": clockin_date.strftime("%Y-%m-%d 08:00"),
            }
        )
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_manager).action_attendance_sheet_done()
        self.test_attendance_open.unlink()

        # TEST09: Test sheet done (As Reviewer)
        sheet.sudo(self.test_user_manager).action_attendance_sheet_done()
        self.assertEqual(sheet.state, "done")

        # TEST10: Test sheet lock
        sheet.sudo(self.test_user_manager).action_attendance_sheet_lock()
        self.assertEqual(sheet.state, "locked")

        # TEST11: Test write sheet when locked
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_employee).write(
                {"date_start": fields.Date.today()}
            )

        # TEST12: Test error trying to write attendance
        with self.assertRaises(UserError):
            self.test_attendance3.write(
                {"check_out": fields.Date.today().strftime("%Y-%m-%d 20:00")}
            )

        # TEST13: Test error trying to delete attendance
        with self.assertRaises(UserError):
            self.test_attendance3.unlink()

        # TEST14: Test sheet unlock
        sheet.sudo(self.test_user_manager).action_attendance_sheet_unlock()
        self.assertEqual(sheet.state, "done")

        # TEST15: Test sheet draft
        sheet.sudo(self.test_user_manager).action_attendance_sheet_draft()
        self.assertEqual(sheet.state, "draft")

        # TEST16: Test sheet done error when in draft
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_manager).action_attendance_sheet_done()

        # TEST17: Test delete attendance
        self.test_attendance3.unlink()
        self.assertEqual(len(sheet.attendance_ids), 2)

        # TEST18: Test sheet refuse
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_manager).action_attendance_sheet_refuse()
        sheet.sudo(self.test_user_employee).action_attendance_sheet_confirm()
        sheet.sudo(self.test_user_manager).action_attendance_sheet_refuse()
        self.assertEqual(sheet.state, "draft")

        # TEST19: Set company date range to bi-weekly
        company.write({"attendance_sheet_range": "BIWEEKLY"})
        self.assertEqual(company.date_end, fields.Date.today() + timedelta(days=13))

        # TEST20: Test autolunch on attendance
        clock_date = fields.Date.today() + timedelta(days=2)
        self.test_attendance4 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": clock_date.strftime("%Y-%m-%d 08:00"),
                "check_out": clock_date.strftime("%Y-%m-%d 16:00"),
            }
        )
        self.assertEqual(self.test_attendance4.auto_lunch, True)

    def test_company_create_sheet_id(self):
        company = self.env.user.company_id
        company.write({"use_attendance_sheets": True})

        # TEST21: Scheduled Action No Company Start/End Date Error
        with self.assertRaises(UserError):
            self.AttendanceSheet._create_sheet_id()

        # TEST22: Company Start/End Date onchange
        company = self.env.user.company_id
        company.write(
            {
                "date_start": fields.Date.today(),
                "attendance_sheet_range": "WEEKLY",
                "attendance_sheet_review_policy": "employee_manager",
            }
        )
        company.onchange_attendance_sheet_range()
        self.assertEqual(company.date_start, fields.Date.today())

        # TEST23: Create Sheets Cron Method
        self.AttendanceSheet._create_sheet_id()
        sheets = self.env["hr.attendance.sheet"].search([])
        self.assertEqual(len(sheets), 2)

        # TEST24: Test _get_possible_reviewers for employee_manager
        sheet = self.env["hr.attendance.sheet"].search([], limit=1)
        self.assertEqual(len(sheet._get_possible_reviewers()), 2)

        # TEST25: Test _get_possible_reviewers for hr_or_manager
        company.write({"attendance_sheet_review_policy": "hr_or_manager"})
        sheet = self.env["hr.attendance.sheet"].search([], limit=1)
        self.assertEqual(len(sheet._get_possible_reviewers()), 4)

        # TEST26: Test confirm button with hr_or_manager policy
        sheet = self.env["hr.attendance.sheet"].search([], limit=1)
        sheet.sudo(self.test_user_employee).action_attendance_sheet_confirm()
        self.assertEqual(sheet.state, "confirm")

    def test_company_create(self):
        # TEST27: Create Company
        company = self.test_company = self.env["res.company"].create(
            {
                "name": "Test Company",
                "date_start": fields.Date.today(),
                "attendance_sheet_range": "BIWEEKLY",
            }
        )
        self.assertEqual(company.date_end, fields.Date.today() + timedelta(days=13))

    def test_company_start_end_date_change(self):
        # TEST28: Test changing start/end date on company via cron
        company = self.env.user.company_id
        company.write(
            {
                "date_start": fields.Date.today() - timedelta(days=7),
                "date_end": fields.Date.today(),
                "use_attendance_sheets": True,
                "attendance_sheet_range": "WEEKLY",
                "attendance_sheet_review_policy": "employee_manager",
            }
        )
        self.AttendanceSheet._create_sheet_id()
        self.assertEqual(company.date_end, fields.Date.today() + timedelta(days=6))

    def test_set_date_end(self):
        # TEST29: Create Company and test else statement in set end date
        company = self.test_company = self.env["res.company"].create(
            {
                "name": "Test Company",
                "date_start": fields.Date.today(),
                "attendance_sheet_range": "DAILY",
            }
        )
        self.assertEqual(
            company.date_end,
            fields.Date.today() + relativedelta(months=1, day=1, days=-1),
        )

    def test_access_errors(self):
        manual_attendance_group = self.env.ref("hr_attendance.group_hr_attendance")
        internal_user_group = self.env.ref("base.group_user")
        self.test_user_basic = self.env["res.users"].create(
            {
                "name": "Test User Employee",
                "login": "basic",
                "email": "basic@test.com",
                "groups_id": [(4, manual_attendance_group.id)],
            }
        )
        self.test_user_basic.write({"groups_id": [(4, internal_user_group.id)]})
        self.test_basic_employee = self.env["hr.employee"].create(
            {
                "name": "TestBasicEmployee",
                "user_id": self.test_user_employee.id,
                "parent_id": self.test_manager.id,
                "manual_attendance": True,
                "use_attendance_sheets": True,
                "hours_to_work": 80,
            }
        )
        self.test_attendance1 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_basic_employee.id,
                "check_in": fields.Date.today().strftime("%Y-%m-%d 08:00"),
                "check_out": fields.Date.today().strftime("%Y-%m-%d 12:00"),
            }
        )

        # Create sheet and confirm then done
        view_id = "hr_attendance_sheet.hr_attendance_sheet_view_form"
        with Form(self.AttendanceSheet, view=view_id) as f:
            f.employee_id = self.test_basic_employee
            f.date_start = fields.Date.today()
            f.date_end = fields.Date.today() + timedelta(days=14)
        sheet = f.save()
        sheet.action_attendance_sheet_confirm()

        # TEST30: errors based on policy
        company = self.env.user.company_id
        company.write({"attendance_sheet_review_policy": "hr"})
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).action_attendance_sheet_refuse()
        company.write({"attendance_sheet_review_policy": "employee_manager"})
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).action_attendance_sheet_refuse()
        company.write({"attendance_sheet_review_policy": "hr_or_manager"})
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).action_attendance_sheet_refuse()

        # TEST31: error if basic employee tries to update approved sheet
        sheet.sudo(self.test_user_manager).action_attendance_sheet_done()
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).write(
                {"date_start": fields.Date.today() + timedelta(days=1)}
            )

        # TEST32: error if basic employee tries to update attendance on approved sheet
        with self.assertRaises(UserError):
            self.test_attendance1.sudo(self.test_user_basic).write(
                {"check_in": fields.Date.today() + timedelta(days=1)}
            )

        # TEST33: permission error locking/unlocking done sheet
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).action_attendance_sheet_lock()
        sheet.sudo(self.test_user_manager).action_attendance_sheet_lock()
        with self.assertRaises(UserError):
            sheet.sudo(self.test_user_basic).action_attendance_sheet_unlock()

    def test_auto_lunch_scenario(self):
        # TEST34: If attendance auto lunch set true when it shouldn't be
        company = self.env.user.company_id
        company.write(
            {
                "use_attendance_sheets": True,
                "auto_lunch": True,
                "auto_lunch_duration": 5,
                "auto_lunch_hours": 0.5,
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today() + timedelta(days=7),
            }
        )
        self.AttendanceSheet._create_sheet_id()
        self.test_attendance_no_lunch = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": (fields.Date.today() + timedelta(days=5)).strftime(
                    "%Y-%m-%d 8:00"
                ),
                "check_out": (fields.Date.today() + timedelta(days=5)).strftime(
                    "%Y-%m-%d 12:00"
                ),
                "auto_lunch": True,
            }
        )
        self.assertEqual(self.test_attendance_no_lunch.auto_lunch, False)

        # TEST35: clock-in button method on sheet
        sheet = self.env["hr.attendance.sheet"].search([], limit=1)
        sheet.attendance_ids.unlink()
        sheet.attendance_action_change()
        self.assertEqual(len(sheet.attendance_ids), 1)

    def test_attendance_admin(self):
        # TEST36: Test possible reviewers with dept admin & employee_manager policy
        company = self.env.user.company_id
        company.write(
            {
                "use_attendance_sheets": True,
                "attendance_sheet_review_policy": "employee_manager",
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today() + timedelta(days=7),
            }
        )
        self.test_admin = self.env["hr.employee"].create({"name": "TestAdmin"})
        self.test_department1 = self.env["hr.department"].create(
            {
                "name": "Test Department",
                "attendance_admin": self.test_admin.id,
            }
        )
        self.test_employee.write({"department_id": self.test_department1.id})
        self.AttendanceSheet._create_sheet_id()
        self.test_attendance_no_lunch = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": (fields.Date.today() + timedelta(days=5)).strftime(
                    "%Y-%m-%d 8:00"
                ),
                "check_out": (fields.Date.today() + timedelta(days=5)).strftime(
                    "%Y-%m-%d 12:00"
                ),
                "auto_lunch": True,
            }
        )
        sheet = self.env["hr.attendance.sheet"].search([], limit=1)
        sheet._get_possible_reviewers()
        self.assertEqual(len(sheet._get_possible_reviewers()), 2)

        # TEST37: Test possible reviewers with dept admin & hr_or_manager policy
        company.write({"attendance_sheet_review_policy": "hr_or_manager"})
        sheet._get_possible_reviewers()
        self.assertEqual(len(sheet._get_possible_reviewers()), 4)

    def test_auto_lunch_time_between_too_small_scenario(self):
        # TEST38: If attendances are within same day but < lunch duration.
        company = self.env.user.company_id
        company.write(
            {
                "use_attendance_sheets": True,
                "auto_lunch": True,
                "auto_lunch_duration": 5,
                "auto_lunch_hours": 1,
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today() + timedelta(days=7),
            }
        )
        self.AttendanceSheet._create_sheet_id()
        self.test_attendance_lunch1 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": (fields.Date.today() + timedelta(days=3)).strftime(
                    "%Y-%m-%d 8:00"
                ),
                "check_out": (fields.Date.today() + timedelta(days=3)).strftime(
                    "%Y-%m-%d 14:00"
                ),
            }
        )
        self.test_attendance_lunch2 = self.env["hr.attendance"].create(
            {
                "employee_id": self.test_employee.id,
                "check_in": (fields.Date.today() + timedelta(days=3)).strftime(
                    "%Y-%m-%d 14:15"
                ),
                "check_out": (fields.Date.today() + timedelta(days=3)).strftime(
                    "%Y-%m-%d 18:15"
                ),
            }
        )
        self.test_attendance_lunch1._compute_duration()
        self.assertEqual(self.test_attendance_lunch1.auto_lunch, True)
