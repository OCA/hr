# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Course Survey",
    "summary": """
        Evaluate a course using a Schedule""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_course", "survey"],
    "data": [
        "data/mail.xml",
        "views/hr_course_attendee.xml",
        "views/hr_course.xml",
        "views/hr_course_schedule.xml",
    ],
    "demo": [],
}
