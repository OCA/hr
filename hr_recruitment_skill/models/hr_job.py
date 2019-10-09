# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    required_skill_ids = fields.Many2many(
        'hr.skill',
        relation='hr_jobs_required_skills',
        string='Required skills'
    )
    desired_skill_ids = fields.Many2many(
        'hr.skill',
        relation='hr_jobs_desired_skills',
        string='Nice to have'
    )
