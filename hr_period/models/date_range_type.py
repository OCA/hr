# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DateRangeType(models.Model):

    _inherit = "date.range.type"

    hr_period = fields.Boolean(string="Is HR period?")
    hr_fiscal_year = fields.Boolean(string="Is HR Fiscal Year?")
