# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.survey.tests import common


class TestHrCourse(common.TestSurveyCommon):
    def setUp(self):
        super(TestHrCourse, self).setUp()
        self.survey = (
            self.env["survey.survey"]
            .with_user(self.survey_manager)
            .create(
                {
                    "title": "Test Survey",
                    "access_mode": "public",
                    "users_login_required": True,
                    "users_can_go_back": False,
                    "state": "open",
                    "scoring_type": "scoring_without_answers",
                }
            )
        )
        self.question = self._add_question(
            self.page_0,
            "Q0",
            "simple_choice",
            survey_id=self.survey.id,
            labels=[
                {"value": "Choice0", "is_correct": True, "answer_score": 100},
                {"value": "Choice1"},
            ],
        )
        self.course_categ = self.env["hr.course.category"].create({"name": "Category1"})
        self.employee1 = self.env["hr.employee"].create({"name": "Employee1"})
        self.employee2 = self.env["hr.employee"].create({"name": "Employee2"})
        self.course = self.env["hr.course"].create(
            {
                "name": "Test Course",
                "category_id": self.course_categ.id,
                "examination_survey_id": self.survey.id,
                "permanence": False,
            }
        )

    def test_hr_schedule(self):
        self.course_schedule = self.env["hr.course.schedule"].create(
            {
                "name": "Test Schedule",
                "course_id": self.course.id,
                "cost": 100,
                "examination_survey_id": self.survey.id,
                "authorized_by": self.employee1.id,
                "start_date": "2019-02-15",
                "end_date": "2019-02-20",
            }
        )
        with self.assertRaises(ValidationError):
            self.course_schedule.write({"end_date": "2019-02-10"})

        self.assertEqual(self.course_schedule.state, "draft")
        self.course_schedule.cancel_course()
        self.assertEqual(self.course_schedule.state, "cancelled")
        self.course_schedule.back2draft()

        self.course_schedule.draft2waiting()
        self.assertEqual(self.course_schedule.state, "waiting_attendees")

        self.course_schedule.attendant_ids = [
            (6, 0, [self.employee1.id, self.employee2.id])
        ]
        self.assertTrue(self.course_schedule.attendant_ids)
        self.assertEqual(len(self.course_schedule.attendant_ids), 2)

        self.course_schedule.waiting2inprogress()
        self.assertEqual(self.course_schedule.state, "in_progress")
        self.assertEqual(len(self.course_schedule.course_attendee_ids), 2)
        self.assertFalse(self.course_schedule.course_attendee_ids[0].survey_answer_id)
        self.course_schedule.attendant_ids = [(2, self.employee2.id, 0)]
        self.course_schedule.waiting2inprogress()
        self.assertEqual(len(self.course_schedule.attendant_ids), 1)
        self.assertEqual(len(self.course_schedule.course_attendee_ids), 1)
        self.employee1._compute_count_courses()
        self.assertEqual(self.employee1.count_courses, 1)
        self.employee1.action_view_course()

        self.course_schedule.inprogress2validation()
        self.assertEqual(self.course_schedule.state, "in_validation")
        self.assertEqual(self.course_schedule.course_attendee_ids.result, "pending")
        with self.assertRaises(ValidationError):
            self.course_schedule.course_attendee_ids.resend_survey()
        answer = self.course_schedule.course_attendee_ids.survey_answer_id
        self.assertTrue(answer.hr_course_attendee_ids)
        self._add_answer_line(
            self.question,
            answer,
            self.question.suggested_answer_ids.filtered(
                lambda l: l.value == "Choice1"
            ).id,
            answer_type="suggestion",
            answer_fname="suggested_answer_id",
        )
        answer._mark_done()
        self.assertEqual(self.course_schedule.course_attendee_ids.result, "failed")
        self.course_schedule.course_attendee_ids.resend_survey()
        self.assertNotEqual(
            answer, self.course_schedule.course_attendee_ids.survey_answer_id
        )
        answer = self.course_schedule.course_attendee_ids.survey_answer_id
        self.assertTrue(answer.hr_course_attendee_ids)
        self._add_answer_line(
            self.question,
            answer,
            self.question.suggested_answer_ids.filtered(
                lambda l: l.value == "Choice0"
            ).id,
            answer_type="suggestion",
            answer_fname="suggested_answer_id",
        )
        answer._mark_done()
        self.assertEqual(self.course_schedule.course_attendee_ids.result, "passed")
        with self.assertRaises(ValidationError):
            self.course_schedule.course_attendee_ids.resend_survey()
