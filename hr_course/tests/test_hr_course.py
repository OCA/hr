# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestHrCourse(common.TransactionCase):

    def setUp(self):
        super(TestHrCourse, self).setUp()
        self.course_categ = self.env['hr.course.category'].create({
            'name': 'Category 1'
        })
        self.employee1 = self.env['hr.employee'].create({
            'name': 'Employee 1'
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Employee 2'
        })
        self.course_id = self.env['hr.course'].create({
            'name': 'Course name',
            'category_id': self.course_categ.id,
            'cost': 100,
            'authorized_by': self.employee1.id,
            'permanence': True,
            'permanence_time': '1 month',
            'start_date': '2019-02-15',
            'end_date': '2019-02-20',
        })

    def test_hr_course(self):
        with self.assertRaises(ValidationError):
            self.course_id.write({'end_date': '2019-02-10'})

        self.assertEqual(self.course_id.state, 'draft')
        self.course_id.permanence = False
        self.course_id._onchange_permanence()
        self.assertFalse(self.course_id.permanence_time)
        self.course_id.cancel_course()
        self.assertEqual(self.course_id.state, 'cancelled')
        self.course_id.back2draft()

        self.course_id.draft2waiting()
        self.assertEqual(self.course_id.state, 'waiting_attendees')
        self.course_id.attendant_ids = [
            (6, 0, [self.employee1.id, self.employee2.id])
        ]
        self.assertTrue(self.course_id.attendant_ids)
        self.assertEqual(len(self.course_id.attendant_ids), 2)

        self.course_id.waiting2inprogress()
        self.assertEqual(self.course_id.state, 'in_progress')
        self.assertEqual(len(self.course_id.course_attendee_ids), 2)
        self.course_id.attendant_ids = [(2, self.employee2.id, 0)]
        self.course_id.waiting2inprogress()
        self.assertEqual(len(self.course_id.attendant_ids), 1)
        self.assertEqual(len(self.course_id.course_attendee_ids), 1)
        self.employee1._compute_count_courses()
        self.assertEqual(self.employee1.count_courses, 1)
        self.employee1.action_view_course()

        self.course_id.inprogress2validation()
        self.assertEqual(self.course_id.state, 'in_validation')
        with self.assertRaises(ValidationError):
            self.course_id.validation2complete()
        self.course_id.all_passed()
        self.assertEqual(
            self.course_id.course_attendee_ids[0].result, 'passed')
        self.course_id.validation2complete()
        self.assertEqual(self.course_id.state, 'completed')
