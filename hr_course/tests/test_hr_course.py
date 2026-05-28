# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestHrCourse(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.course_categ = self.env["hr.course.category"].create(
            {"name": "Category 1"}
        )
        self.employee1 = self.env["hr.employee"].create({"name": "Employee 1"})
        self.employee2 = self.env["hr.employee"].create({"name": "Employee 2"})
        self.course_id = self.env["hr.course"].create(
            {
                "name": "Course name",
                "category_id": self.course_categ.id,
                "permanence": True,
                "permanence_time": "1 month",
            }
        )
        self.course_schedule_id = self.env["hr.course.schedule"].create(
            {
                "name": "Convocatory",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
                "start_date": "2019-02-15",
                "end_date": "2019-02-20",
            }
        )

    def test_hr_course(self):
        self.course_id.permanence = False
        self.course_id._onchange_permanence()
        self.assertFalse(self.course_id.permanence_time)

    def test_hr_course_code_auto(self):
        course = self.env["hr.course"].create(
            {
                "name": "Course with code",
                "category_id": self.course_categ.id,
            }
        )
        self.assertTrue(course.code)
        self.assertTrue(course.code.startswith("C"))

    def test_hr_course_schedule_code_auto(self):
        schedule = self.env["hr.course.schedule"].create(
            {
                "name": "Schedule with code",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
            }
        )
        self.assertTrue(schedule.code)
        self.assertTrue(schedule.code.startswith("CS"))

    def test_hr_course_code_unique(self):
        self.env["hr.course"].create(
            {
                "name": "Course 1",
                "category_id": self.course_categ.id,
                "code": "UNIQUE-CODE",
            }
        )
        with self.assertRaises(psycopg2.IntegrityError):
            self.env["hr.course"].create(
                {
                    "name": "Course 2",
                    "category_id": self.course_categ.id,
                    "code": "UNIQUE-CODE",
                }
            )

    def test_hr_course_name_search_by_code(self):
        course = self.env["hr.course"].create(
            {
                "name": "Searchable Course",
                "category_id": self.course_categ.id,
                "code": "SEARCH-123",
            }
        )
        result = self.env["hr.course"].name_search("SEARCH-123")
        self.assertIn(course.id, [r[0] for r in result])

    def test_hr_course_name_search_fallback(self):
        course = self.env["hr.course"].create(
            {
                "name": "Fallback Course",
                "category_id": self.course_categ.id,
                "code": "FALL-001",
            }
        )
        result = self.env["hr.course"].name_search("Fallback Course")
        self.assertIn(course.id, [r[0] for r in result])

    def test_hr_course_display_name(self):
        course_both = self.env["hr.course"].create(
            {
                "name": "Named Course",
                "category_id": self.course_categ.id,
                "code": "CODE-1",
            }
        )
        self.assertEqual(course_both.display_name, "[CODE-1] Named Course")

        course_name_only = self.env["hr.course"].create(
            {
                "name": "Name Only",
                "category_id": self.course_categ.id,
            }
        )
        course_name_only.code = False
        self.assertEqual(course_name_only.display_name, "Name Only")

    def test_hr_course_explicit_code(self):
        course = self.env["hr.course"].create(
            {
                "name": "Explicit Code",
                "category_id": self.course_categ.id,
                "code": "MY-CODE",
            }
        )
        self.assertEqual(course.code, "MY-CODE")

    def test_hr_course_schedule_display_name(self):
        schedule_both = self.env["hr.course.schedule"].create(
            {
                "name": "Named Schedule",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
                "code": "SCH-1",
            }
        )
        self.assertEqual(schedule_both.display_name, "[SCH-1] Named Schedule")

        schedule_name_only = self.env["hr.course.schedule"].create(
            {
                "name": "Name Only Schedule",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
            }
        )
        schedule_name_only.code = False
        self.assertEqual(schedule_name_only.display_name, "Name Only Schedule")

    def test_hr_course_schedule_name_search(self):
        schedule = self.env["hr.course.schedule"].create(
            {
                "name": "Searchable Schedule",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
                "code": "SCH-SEARCH",
            }
        )
        result = self.env["hr.course.schedule"].name_search("SCH-SEARCH")
        self.assertIn(schedule.id, [r[0] for r in result])

        result_fallback = self.env["hr.course.schedule"].name_search(
            "Searchable Schedule"
        )
        self.assertIn(schedule.id, [r[0] for r in result_fallback])

    def test_hr_course_schedule_code_unique(self):
        self.env["hr.course.schedule"].create(
            {
                "name": "Schedule 1",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
                "code": "UNIQUE-SCH",
            }
        )
        with self.assertRaises(psycopg2.IntegrityError):
            self.env["hr.course.schedule"].create(
                {
                    "name": "Schedule 2",
                    "course_id": self.course_id.id,
                    "cost": 100,
                    "authorized_by": self.employee1.id,
                    "code": "UNIQUE-SCH",
                }
            )

    def test_hr_course_schedule_explicit_code(self):
        schedule = self.env["hr.course.schedule"].create(
            {
                "name": "Explicit Schedule",
                "course_id": self.course_id.id,
                "cost": 100,
                "authorized_by": self.employee1.id,
                "code": "MY-SCH-CODE",
            }
        )
        self.assertEqual(schedule.code, "MY-SCH-CODE")

    def test_hr_course_schedule(self):
        with self.assertRaises(ValidationError):
            self.course_schedule_id.write({"end_date": "2019-02-10"})

        self.assertEqual(self.course_schedule_id.state, "draft")
        self.course_schedule_id.cancel_course()
        self.assertEqual(self.course_schedule_id.state, "cancelled")
        self.course_schedule_id.back2draft()

        self.course_schedule_id.draft2waiting()
        self.assertEqual(self.course_schedule_id.state, "waiting_attendees")
        self.course_schedule_id.attendant_ids = [
            (6, 0, [self.employee1.id, self.employee2.id])
        ]
        self.assertTrue(self.course_schedule_id.attendant_ids)
        self.assertEqual(len(self.course_schedule_id.attendant_ids), 2)

        self.course_schedule_id.waiting2inprogress()
        self.assertEqual(self.course_schedule_id.state, "in_progress")
        self.assertEqual(len(self.course_schedule_id.course_attendee_ids), 2)
        self.course_schedule_id.attendant_ids = [(2, self.employee2.id, 0)]
        self.course_schedule_id.waiting2inprogress()
        self.assertEqual(len(self.course_schedule_id.attendant_ids), 1)
        self.assertEqual(len(self.course_schedule_id.course_attendee_ids), 1)
        self.employee1._compute_count_courses()
        self.assertEqual(self.employee1.count_courses, 1)
        self.employee1.action_view_course()

        self.course_schedule_id.inprogress2validation()
        self.assertEqual(self.course_schedule_id.state, "in_validation")
        with self.assertRaises(ValidationError):
            self.course_schedule_id.validation2complete()
        self.course_schedule_id.all_passed()
        self.assertEqual(
            self.course_schedule_id.course_attendee_ids[0].result, "passed"
        )
        self.course_schedule_id.validation2complete()
        self.assertEqual(self.course_schedule_id.state, "completed")
