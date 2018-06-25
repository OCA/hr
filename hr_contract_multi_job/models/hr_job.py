# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    contract_job_ids = fields.One2many(
        'hr.contract.job',
        'job_id',
        string='Contract Jobs')
