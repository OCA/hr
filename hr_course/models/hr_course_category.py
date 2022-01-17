# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HRCourseCategory(models.Model):
    _name = "hr.course.category"
    _description = "Course Category"

    name = fields.Char(string="Course category", required=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Category already exists !")]
